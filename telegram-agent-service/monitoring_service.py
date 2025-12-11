"""
Automated Air Quality News Monitoring Service
- Monitors Telegram channels every 3 hours
- Translates posts to RU/UZ/EN
- Sends to moderation group via Telegram Bot
- Publishes approved news to Firebase
- Auto-deletes news older than 7 days
"""

import os
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv

# Telegram
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

# Translation
from deep_translator import GoogleTranslator

# Scheduling
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Firebase
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# Playwright for screenshots
from playwright.async_api import async_playwright

# Import web search agent for fallback when no Telegram news found
from web_search_agent import search_web_for_news

load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_API_ID = int(os.getenv('TELEGRAM_API_ID', '0'))
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH', '')
SESSION_NAME = 'air_quality_bot'

BOT_TOKEN = '8333357201:AAFc4DBdgbbxH_mT4wJMZ8ieLGY_s3Zg0x8'
MODERATION_CHAT_ID = 832620295  # Direct to user for testing

CHANNELS = os.getenv('CHANNELS_TO_MONITOR', '').split(',')

# Keywords for air quality - more specific to avoid false positives
AIR_QUALITY_KEYWORDS = [
    # Russian - specific phrases
    'качество воздуха', 'загрязнение воздуха', 'воздух загрязнен', 'чистота воздуха',
    'смог', 'выбросы в атмосферу', 'pm2.5', 'pm10', 'aqi',
    'мониторинг воздуха', 'экология воздух', 'озон',

    # Uzbek - specific phrases
    'havo sifati', 'havo iflosligi', 'iflos havo', 'havo tozaligi',
    'tutun', 'atmosfera iflosligi', 'chang',
    'havo monitoringi', 'ekologiya havo',

    # English - specific phrases
    'air quality', 'air pollution', 'polluted air', 'air monitoring',
    'smog', 'atmospheric emissions', 'air cleanliness'
]

# Firebase setup
FIREBASE_CREDS_PATH = os.getenv('FIREBASE_CREDS_PATH', 'firebase-creds.json')
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDS_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Translator is created per request (GoogleTranslator doesn't need global instance)

# Telethon client
tg_client = TelegramClient(SESSION_NAME, TELEGRAM_API_ID, TELEGRAM_API_HASH)

# Bot
bot = Bot(token=BOT_TOKEN)

# Storage for pending posts
pending_posts = {}

# SQLite for tracking
import sqlite3

def init_monitoring_db():
    """Initialize database for monitoring"""
    conn = sqlite3.connect('monitoring.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS monitored_posts (
            message_id INTEGER,
            channel TEXT,
            processed_at TIMESTAMP,
            status TEXT,
            PRIMARY KEY (message_id, channel)
        )
    ''')
    conn.commit()
    conn.close()

def is_already_monitored(channel: str, message_id: int) -> bool:
    """Check if post was already processed"""
    conn = sqlite3.connect('monitoring.db')
    c = conn.cursor()
    c.execute('SELECT 1 FROM monitored_posts WHERE channel = ? AND message_id = ?', (channel, message_id))
    result = c.fetchone()
    conn.close()
    return result is not None

def mark_as_monitored(channel: str, message_id: int, status: str = 'pending'):
    """Mark post as monitored"""
    conn = sqlite3.connect('monitoring.db')
    c = conn.cursor()
    c.execute(
        'INSERT OR REPLACE INTO monitored_posts (channel, message_id, processed_at, status) VALUES (?, ?, ?, ?)',
        (channel, message_id, datetime.now(), status)
    )
    conn.commit()
    conn.close()

def contains_air_quality_keywords(text: str) -> bool:
    """Check if text contains air quality keywords"""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in AIR_QUALITY_KEYWORDS)

async def translate_text(text: str, dest_lang: str) -> str:
    """Translate text to target language"""
    try:
        translator = GoogleTranslator(source='auto', target=dest_lang)
        return translator.translate(text)
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text

async def translate_post(text: str) -> Dict[str, str]:
    """Translate post to all 3 languages"""
    translations = {}

    # Russian
    translations['ru'] = await translate_text(text, 'ru')

    # Uzbek
    translations['uz'] = await translate_text(text, 'uz')

    # English
    translations['en'] = await translate_text(text, 'en')

    return translations

async def download_post_photo(client, message, output_path: str):
    """Download photo from message"""
    if message.media and isinstance(message.media, MessageMediaPhoto):
        try:
            await client.download_media(message.media, output_path)
            return output_path
        except Exception as e:
            logger.error(f"Failed to download photo: {e}")
            return None
    return None

async def create_preview_page(post_data: Dict[str, Any]) -> str:
    """Create preview page and return URL"""
    post_id = post_data['id']

    # Save to Firebase in 'news_preview' collection
    try:
        preview_ref = db.collection('news_preview')
        preview_ref.document(post_id).set({
            'id': post_id,
            'channel': post_data['channel'],
            'date': post_data['date'],
            'text': post_data['text'],
            'translations': post_data['translations'],
            'link': post_data.get('link', ''),
            'createdAt': firestore.SERVER_TIMESTAMP
        })
        logger.info(f"💾 Saved preview to Firebase: {post_id}")
    except Exception as e:
        logger.error(f"Failed to save preview to Firebase: {e}")

    # Return Vercel preview URL (API route - now using ngrok for local dev)
    VERCEL_URL = os.getenv('VERCEL_PREVIEW_URL', 'https://petiolar-mallory-apostolically.ngrok-free.dev')
    return f'{VERCEL_URL}/api/news/{post_id}'

async def take_screenshot(url: str, output_path: str):
    """Take screenshot of webpage"""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_load_state('networkidle')
            await page.screenshot(path=output_path, full_page=True)
            await browser.close()
        return output_path
    except Exception as e:
        logger.error(f"Screenshot error: {e}")
        return None

async def send_to_moderation(post_data: Dict[str, Any], screenshot_path: str, preview_url: str):
    """Send post to moderation chat"""
    global MODERATION_CHAT_ID

    if not MODERATION_CHAT_ID:
        logger.error("MODERATION_CHAT_ID not set")
        return

    # Prepare message (Russian only)
    # Escape underscores for Markdown
    escaped_url = preview_url.replace('_', '\\_')

    message_text = f"""
🆕 **Новость о качестве воздуха**

📍 {post_data['channel']}

{post_data['translations']['ru'][:400]}...

🔗 Полный текст: {escaped_url}
"""

    # Buttons
    keyboard = [
        [InlineKeyboardButton("✅ Запостить", callback_data=f"approve_{post_data['id']}")],
        [InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{post_data['id']}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send photo (screenshot or original post photo)
    try:
        if screenshot_path and os.path.exists(screenshot_path):
            with open(screenshot_path, 'rb') as photo:
                await bot.send_photo(
                    chat_id=MODERATION_CHAT_ID,
                    photo=photo,
                    caption=message_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
        else:
            # Send as text message if no photo
            await bot.send_message(
                chat_id=MODERATION_CHAT_ID,
                text=message_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        logger.info(f"✅ Sent to moderation: {post_data['id']}")
    except Exception as e:
        logger.error(f"Failed to send to moderation: {e}")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()

    data = query.data
    action, post_id = data.split('_', 1)

    if action == 'approve':
        # Save to Firebase
        await save_to_firebase(post_id)
        await query.edit_message_caption(
            caption=query.message.caption + "\n\n✅ **ОПУБЛИКОВАНО**",
            parse_mode='Markdown'
        )
        logger.info(f"✅ Approved and published: {post_id}")

    elif action == 'reject':
        # Delete the message instead of marking
        try:
            await query.message.delete()
            logger.info(f"🗑️ Deleted rejected post: {post_id}")
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
            # Fallback - mark as rejected
            await query.edit_message_caption(
                caption=query.message.caption + "\n\n❌ **ОТКЛОНЕНО**",
                parse_mode='Markdown'
            )

        # Clean up pending posts
        if post_id in pending_posts:
            del pending_posts[post_id]

async def save_to_firebase(post_id: str):
    """Save approved post to Firebase"""
    if post_id not in pending_posts:
        logger.error(f"Post {post_id} not found in pending")
        return

    post_data = pending_posts[post_id]

    # Save to 'news' collection (same as frontend uses)
    news_ref = db.collection('news')

    news_doc = {
        'id': post_id,
        'titleKey': post_id + '_title',
        'summaryKey': post_id + '_summary',
        'source': post_data['channel'],
        'time': post_data['date'],
        'tag': 'Air Quality',
        'translations': post_data['translations'],
        'originalLink': post_data.get('link', ''),
        'createdAt': firestore.SERVER_TIMESTAMP
    }

    news_ref.document(post_id).set(news_doc)
    logger.info(f"✅ Saved to Firebase: {post_id}")

    # Clean up
    del pending_posts[post_id]

async def delete_old_news():
    """Delete news older than 7 days"""
    seven_days_ago = datetime.now() - timedelta(days=7)

    news_ref = db.collection('news')
    old_news = news_ref.where(
        filter=FieldFilter('createdAt', '<', seven_days_ago)
    ).stream()

    count = 0
    for doc in old_news:
        doc.reference.delete()
        count += 1

    if count > 0:
        logger.info(f"🗑️  Deleted {count} old news posts")

async def monitor_channels():
    """Monitor channels for new air quality posts"""
    logger.info("🔄 Starting monitoring cycle...")

    await tg_client.start()

    new_posts_count = 0

    for channel in CHANNELS:
        channel = channel.strip()
        if not channel:
            continue

        try:
            # Get last 5 messages (last 3 hours)
            messages = await tg_client.get_messages(channel, limit=5)

            for msg in messages:
                if not msg.message:
                    continue

                # Check if already processed
                if is_already_monitored(channel, msg.id):
                    continue

                # Check if contains air quality keywords
                if not contains_air_quality_keywords(msg.message):
                    continue

                logger.info(f"📰 New post found: {channel}/{msg.id}")

                # Create post data
                post_id = f"{channel.replace('@', '')}_{msg.id}_{int(datetime.now().timestamp())}"

                # Translate
                translations = await translate_post(msg.message)

                post_data = {
                    'id': post_id,
                    'channel': channel,
                    'message_id': msg.id,
                    'date': msg.date.isoformat(),
                    'text': msg.message,
                    'translations': translations,
                    'link': f'https://t.me/{channel.replace("@", "")}/{msg.id}'
                }

                # Download photo if exists
                if msg.media:
                    photo_path = f'/tmp/{post_id}.jpg'
                    await download_post_photo(tg_client, msg, photo_path)
                    post_data['photo'] = photo_path

                # Create preview page
                preview_url = await create_preview_page(post_data)

                # Take screenshot (optional - skip if fails)
                screenshot_path = f'/tmp/{post_id}_screenshot.png'
                screenshot_result = await take_screenshot(preview_url, screenshot_path)

                # If screenshot failed, send without it (send photo from post instead)
                if not screenshot_result and msg.media:
                    screenshot_path = post_data.get('photo', None)

                # Store in pending
                pending_posts[post_id] = post_data

                # Send to moderation
                await send_to_moderation(post_data, screenshot_path, preview_url)

                # Mark as monitored
                mark_as_monitored(channel, msg.id, 'pending')

                new_posts_count += 1

        except Exception as e:
            logger.error(f"Error monitoring {channel}: {e}")

    # If no posts found in Telegram channels, fallback to web search
    if new_posts_count == 0:
        logger.info("No news found in Telegram channels, falling back to web search...")
        await process_web_search_news()

    logger.info(f"✅ Monitoring cycle complete. Found {new_posts_count} new posts")

    await tg_client.disconnect()


async def process_web_search_news():
    """Search web for air quality news and send to moderation"""
    try:
        web_news = await search_web_for_news()

        if not web_news:
            logger.warning("Web search returned no results")
            return

        logger.info(f"🌐 Found {len(web_news)} news from web search")

        for news in web_news:
            try:
                post_id = news['id']

                # Create translations from the news text
                text_for_translation = f"{news.get('title', '')}\n\n{news.get('text', '')}"
                translations = await translate_post(text_for_translation)

                post_data = {
                    'id': post_id,
                    'channel': 'web_search',
                    'message_id': post_id,
                    'date': news.get('date', datetime.now().isoformat()),
                    'text': text_for_translation,
                    'translations': translations,
                    'link': news.get('source_url', ''),
                    'from_web_search': True
                }

                # Use downloaded photo if available
                if news.get('photo_path'):
                    post_data['photo'] = news['photo_path']

                # Create preview page
                preview_url = await create_preview_page(post_data)

                # Take screenshot
                screenshot_path = f'/tmp/{post_id}_screenshot.png'
                screenshot_result = await take_screenshot(preview_url, screenshot_path)

                # If screenshot failed, use the downloaded photo
                if not screenshot_result and news.get('photo_path'):
                    screenshot_path = news['photo_path']

                # Store in pending
                pending_posts[post_id] = post_data

                # Send to moderation
                await send_to_moderation(post_data, screenshot_path, preview_url)

                logger.info(f"✅ Sent web search news to moderation: {post_id}")

            except Exception as e:
                logger.error(f"Error processing web search news item: {e}")
                continue

    except Exception as e:
        logger.error(f"Web search failed: {e}")

async def main():
    """Main service loop"""
    logger.info("🚀 Starting Air Quality News Monitoring Service")

    # Initialize
    init_monitoring_db()

    # Setup bot handlers
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Start bot in background
    await application.initialize()
    await application.start()

    # Setup scheduler
    scheduler = AsyncIOScheduler()

    # Monitor every 3 hours
    scheduler.add_job(monitor_channels, 'interval', hours=3)

    # Clean old news daily
    scheduler.add_job(delete_old_news, 'cron', hour=0, minute=0)

    # Run first monitoring immediately
    await monitor_channels()

    # Start scheduler
    scheduler.start()

    logger.info("✅ Service started successfully")
    logger.info("📊 Monitoring every 3 hours")
    logger.info("🗑️  Cleaning old news daily at midnight")

    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
        scheduler.shutdown()
        await application.stop()
        await application.shutdown()

if __name__ == '__main__':
    asyncio.run(main())
