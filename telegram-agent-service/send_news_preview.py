"""
Send air quality news via Telegram Bot with news-preview links
1. Analyze channels for air quality news
2. Save to Firebase news_preview collection
3. Send preview link via Telegram Bot
"""

import os
import asyncio
import uuid
from datetime import datetime, timedelta
import logging
import httpx

from dotenv import load_dotenv
load_dotenv()

from telethon import TelegramClient
from telethon.tl.types import Message

import firebase_admin
from firebase_admin import credentials, firestore

from air_quality_agent import get_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telethon for reading channels
API_ID = int(os.getenv('TELEGRAM_API_ID', '0'))
API_HASH = os.getenv('TELEGRAM_API_HASH', '')
SESSION_NAME = 'air_quality_bot'

# Bot for sending messages
BOT_TOKEN = '8333357201:AAFc4DBdgbbxH_mT4wJMZ8ieLGY_s3Zg0x8'
TARGET_USER_ID = 832620295

# News preview URL
NEWS_PREVIEW_URL = "https://news-preview-rho.vercel.app/api/news"

CHANNELS_TO_MONITOR = ['@kunuzofficial', '@uza_uz', '@Daryo', '@zamonuz']
MIN_CONFIDENCE = 0.6

# Firebase setup
FIREBASE_CREDS_PATH = 'firebase-creds.json'
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDS_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()


async def send_telegram_message(text: str):
    """Send message via Telegram Bot API"""
    async with httpx.AsyncClient() as client:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': TARGET_USER_ID,
            'text': text,
            'parse_mode': 'HTML',
            'disable_web_page_preview': False
        }
        response = await client.post(url, data=data)
        if response.status_code != 200:
            logger.error(f"Telegram API error: {response.text}")
        return response.status_code == 200


def save_news_to_firebase(news_data: dict, agent) -> str:
    """Save news to Firebase with translations and return document ID"""
    doc_id = str(uuid.uuid4())[:8]

    ru_text = news_data['rephrased']

    # Generate translations
    logger.info(f"Translating to Uzbek...")
    uz_text = agent.translate_text(ru_text, 'uz') or ''

    logger.info(f"Translating to English...")
    en_text = agent.translate_text(ru_text, 'en') or ''

    doc_data = {
        'id': doc_id,
        'channel': news_data['channel'],
        'text': ru_text,
        'original_text': news_data['original'][:500],
        'date': datetime.now().isoformat(),
        'confidence': news_data['confidence'],
        'translations': {
            'ru': ru_text,
            'uz': uz_text,
            'en': en_text
        },
        'status': 'pending',
        'created_at': firestore.SERVER_TIMESTAMP
    }

    db.collection('news_preview').document(doc_id).set(doc_data)
    logger.info(f"Saved news to Firebase: {doc_id}")

    return doc_id


async def main():
    logger.info("Starting news analysis...")

    # Initialize Telethon for reading channels
    tg_client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await tg_client.start()

    try:
        # Send start message
        await send_telegram_message(
            "🔍 <b>Анализ новостей о качестве воздуха</b>\n\n"
            "Ищу релевантные новости за последние 48 часов..."
        )

        agent = get_agent()
        found_news = []
        cutoff_time = datetime.now() - timedelta(hours=48)

        for channel in CHANNELS_TO_MONITOR:
            try:
                logger.info(f"Checking {channel}...")

                async for message in tg_client.iter_messages(channel, limit=30):
                    if not isinstance(message, Message):
                        continue

                    if message.date.replace(tzinfo=None) < cutoff_time:
                        break

                    text = message.text or ""
                    if len(text) < 50:
                        continue

                    try:
                        analysis = agent.is_air_quality_news(text)

                        if analysis.get('is_air_quality_news') and analysis.get('confidence', 0) >= MIN_CONFIDENCE:
                            logger.info(f"Found relevant post in {channel}")

                            # Rephrase
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
            await send_telegram_message(
                "❌ <b>Результат</b>\n\n"
                "Не найдено релевантных новостей о качестве воздуха за последние 48 часов."
            )
        else:
            await send_telegram_message(
                f"✅ <b>Найдено {len(found_news)} новостей!</b>\n\n"
                "Отправляю ссылки на превью..."
            )

            for i, news in enumerate(found_news):
                # Save to Firebase with translations
                doc_id = save_news_to_firebase(news, agent)

                # Generate preview URL
                preview_url = f"{NEWS_PREVIEW_URL}/{doc_id}"

                # Send message with link
                msg = (
                    f"📰 <b>Новость #{i+1}</b>\n"
                    f"📢 Источник: {news['channel']}\n"
                    f"📊 Уверенность: {news['confidence']:.0%}\n\n"
                    f"<b>Превью:</b>\n{preview_url}\n\n"
                    f"<i>Текст:</i> {news['rephrased'][:200]}..."
                )

                await send_telegram_message(msg)
                await asyncio.sleep(1)

            # Final summary
            await send_telegram_message(
                f"📋 <b>Итого</b>\n\n"
                f"• Найдено новостей: {len(found_news)}\n"
                f"• Проверено каналов: {len(CHANNELS_TO_MONITOR)}\n\n"
                f"Нажмите на ссылки превью чтобы посмотреть новости.\n"
                f"Хотите опубликовать какую-то из них в @musaffo_news?"
            )

        logger.info(f"Done! Found {len(found_news)} news")

    finally:
        await tg_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
