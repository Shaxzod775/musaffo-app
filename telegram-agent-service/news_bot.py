"""
News Bot - Find air quality news and publish to frontend via Firebase
Features:
1. Search for air quality news in Telegram channels
2. Send news with inline buttons (Publish / Reject)
3. On publish - save to Firebase 'news' collection (same as frontend)
4. On reject - delete the message
"""

import os
import asyncio
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from telethon import TelegramClient
from telethon.tl.types import Message

import firebase_admin
from firebase_admin import credentials, firestore

from air_quality_agent import get_agent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Telegram Bot Token (Musaffo News Bot)
BOT_TOKEN = os.getenv('NEWS_BOT_TOKEN', '8333357201:AAFc4DBdgbbxH_mT4wJMZ8ieLGY_s3Zg0x8')

# Telethon credentials (for reading channels)
API_ID = int(os.getenv('TELEGRAM_API_ID', '0'))
API_HASH = os.getenv('TELEGRAM_API_HASH', '')
SESSION_NAME = 'air_quality_bot'

# Admin user ID who can publish news
ADMIN_USER_ID = 832620295

# Channels to monitor
CHANNELS_TO_MONITOR = ['@kunuzofficial', '@uza_uz', '@Daryo', '@zamonuz']
MIN_CONFIDENCE = 0.6

# Firebase setup
FIREBASE_CREDS_PATH = 'firebase-creds.json'
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDS_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Store pending news temporarily (news_id -> news_data)
pending_news = {}


def generate_news_id() -> str:
    """Generate short unique ID for news"""
    return str(uuid.uuid4())[:8]


def get_tag_from_channel(channel: str) -> str:
    """Determine news tag based on channel"""
    channel_tags = {
        '@kunuzofficial': 'Global',
        '@uza_uz': 'Gov',
        '@Daryo': 'Global',
        '@zamonuz': 'Tech',
        '@MyGovUz': 'Gov',
        '@toshkent': 'Gov',
    }
    return channel_tags.get(channel, 'Global')


async def search_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search for air quality news in channels"""
    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("У вас нет доступа к этой команде.")
        return

    await update.message.reply_text(
        "🔍 *Поиск новостей о качестве воздуха*\n\n"
        "Анализирую последние 10 постов в каждом канале...",
        parse_mode='Markdown'
    )

    # Initialize Telethon client
    tg_client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await tg_client.start()

    try:
        agent = get_agent()
        found_news = []

        for channel in CHANNELS_TO_MONITOR:
            try:
                logger.info(f"Checking {channel}...")

                async for message in tg_client.iter_messages(channel, limit=10):
                    if not isinstance(message, Message):
                        continue

                    text = message.text or ""
                    if len(text) < 50:
                        continue

                    try:
                        analysis = agent.is_air_quality_news(text)

                        if analysis.get('is_air_quality_news') and analysis.get('confidence', 0) >= MIN_CONFIDENCE:
                            logger.info(f"Found relevant post in {channel}")

                            # Rephrase the news
                            rephrased = agent.rephrase_news(text)

                            found_news.append({
                                'channel': channel,
                                'original': text,
                                'rephrased': rephrased or text,
                                'confidence': analysis.get('confidence', 0),
                                'message_id': message.id
                            })

                    except Exception as e:
                        logger.error(f"Analysis error: {e}")
                        continue

            except Exception as e:
                logger.error(f"Channel {channel} error: {e}")
                continue

        if not found_news:
            await update.message.reply_text(
                "❌ *Результат*\n\n"
                "Не найдено релевантных новостей о качестве воздуха за последние 48 часов.",
                parse_mode='Markdown'
            )
            return

        await update.message.reply_text(
            f"✅ *Найдено {len(found_news)} новостей!*\n\n"
            "Отправляю каждую для проверки...",
            parse_mode='Markdown'
        )

        # Send each news with inline buttons
        for i, news in enumerate(found_news):
            news_id = generate_news_id()

            # Generate translations
            ru_text = news['rephrased']
            logger.info(f"Translating news {news_id} to Uzbek...")
            uz_text = agent.translate_text(ru_text, 'uz') or ''
            logger.info(f"Translating news {news_id} to English...")
            en_text = agent.translate_text(ru_text, 'en') or ''

            # Store pending news with translations
            pending_news[news_id] = {
                'id': news_id,
                'channel': news['channel'],
                'text_ru': ru_text,
                'text_uz': uz_text,
                'text_en': en_text,
                'original': news['original'][:500],
                'confidence': news['confidence'],
                'tag': get_tag_from_channel(news['channel']),
            }

            # Create inline keyboard
            keyboard = [
                [
                    InlineKeyboardButton("✅ Опубликовать", callback_data=f"publish_{news_id}"),
                    InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{news_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Format message
            message_text = (
                f"📰 *Новость #{i+1}*\n"
                f"📢 Источник: {news['channel']}\n"
                f"📊 Уверенность: {news['confidence']:.0%}\n"
                f"🏷 Тег: {pending_news[news_id]['tag']}\n\n"
                f"*Текст (RU):*\n{ru_text[:500]}{'...' if len(ru_text) > 500 else ''}\n\n"
                f"*Текст (UZ):*\n{uz_text[:300]}{'...' if len(uz_text) > 300 else ''}"
            )

            await update.message.reply_text(
                message_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )

            await asyncio.sleep(1)  # Avoid rate limiting

        logger.info(f"Sent {len(found_news)} news for review")

    finally:
        await tg_client.disconnect()


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await query.edit_message_text("У вас нет доступа.")
        return

    data = query.data

    if data.startswith("publish_"):
        news_id = data.replace("publish_", "")
        await publish_news(query, news_id)

    elif data.startswith("reject_"):
        news_id = data.replace("reject_", "")
        await reject_news(query, news_id)


async def publish_news(query, news_id: str):
    """Publish news to Firebase"""
    if news_id not in pending_news:
        await query.edit_message_text("❌ Новость не найдена или уже обработана.")
        return

    news_data = pending_news[news_id]

    try:
        # Create news document for Firebase (matches frontend NewsItem structure)
        now = datetime.now()
        doc_data = {
            'id': news_id,
            'title': news_data['text_ru'][:100],  # First 100 chars as title
            'summary': news_data['text_ru'],
            'source': news_data['channel'],
            'time': now.strftime('%d.%m.%Y'),
            'tag': news_data['tag'],
            # Translations
            'title_ru': news_data['text_ru'][:100],
            'title_uz': news_data['text_uz'][:100] if news_data['text_uz'] else '',
            'title_en': news_data['text_en'][:100] if news_data['text_en'] else '',
            'summary_ru': news_data['text_ru'],
            'summary_uz': news_data['text_uz'] or '',
            'summary_en': news_data['text_en'] or '',
            # Metadata
            'created_at': firestore.SERVER_TIMESTAMP,
            'published': True,
        }

        # Save to 'news' collection (same as frontend uses)
        db.collection('news').document(news_id).set(doc_data)

        # Remove from pending
        del pending_news[news_id]

        logger.info(f"Published news {news_id} to Firebase")

        await query.edit_message_text(
            f"✅ *Новость опубликована!*\n\n"
            f"ID: `{news_id}`\n"
            f"Тег: {doc_data['tag']}\n\n"
            f"Новость появится в приложении Musaffo.",
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"Failed to publish news {news_id}: {e}")
        await query.edit_message_text(f"❌ Ошибка публикации: {e}")


async def reject_news(query, news_id: str):
    """Reject and delete news"""
    if news_id in pending_news:
        del pending_news[news_id]

    logger.info(f"Rejected news {news_id}")

    await query.edit_message_text(
        "🗑 *Новость отклонена*\n\n"
        "Сообщение будет удалено.",
        parse_mode='Markdown'
    )

    # Delete message after 2 seconds
    await asyncio.sleep(2)
    try:
        await query.message.delete()
    except Exception as e:
        logger.error(f"Failed to delete message: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user_id = update.effective_user.id

    if user_id == ADMIN_USER_ID:
        await update.message.reply_text(
            "👋 *Musaffo News Bot*\n\n"
            "Доступные команды:\n"
            "/search - Найти новости о качестве воздуха\n"
            "/help - Помощь",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "👋 Привет! Этот бот предназначен для управления новостями Musaffo."
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler"""
    await update.message.reply_text(
        "*Musaffo News Bot - Справка*\n\n"
        "🔍 /search - Поиск новостей о качестве воздуха в Telegram каналах\n\n"
        "После поиска бот отправит найденные новости с кнопками:\n"
        "• ✅ Опубликовать - сохранить в Firebase и показать в приложении\n"
        "• ❌ Отклонить - удалить сообщение\n\n"
        "Новости автоматически переводятся на RU, UZ и EN.",
        parse_mode='Markdown'
    )


def main():
    """Run the bot"""
    logger.info("Starting Musaffo News Bot...")

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search_news))
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Run bot
    logger.info("Bot is running. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
