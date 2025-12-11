"""
Send air quality news via Telegram Bot (not Telethon user account)
"""

import os
import asyncio
from datetime import datetime, timedelta
import logging
import httpx

from dotenv import load_dotenv
load_dotenv()

from telethon import TelegramClient
from telethon.tl.types import Message

from air_quality_agent import get_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telethon for reading channels (user account)
API_ID = int(os.getenv('TELEGRAM_API_ID', '0'))
API_HASH = os.getenv('TELEGRAM_API_HASH', '')
SESSION_NAME = 'air_quality_bot'

# Bot for sending messages
BOT_TOKEN = '8333357201:AAFc4DBdgbbxH_mT4wJMZ8ieLGY_s3Zg0x8'
TARGET_USER_ID = 832620295

CHANNELS_TO_MONITOR = ['@kunuzofficial', '@uza_uz', '@Daryo', '@zamonuz']
MIN_CONFIDENCE = 0.6


async def send_telegram_message(text: str, photo_path: str = None):
    """Send message via Telegram Bot API using httpx"""
    async with httpx.AsyncClient() as client:
        if photo_path:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            with open(photo_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    'chat_id': TARGET_USER_ID,
                    'caption': text[:1024],
                    'parse_mode': 'Markdown'
                }
                response = await client.post(url, data=data, files=files)
        else:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': TARGET_USER_ID,
                'text': text,
                'parse_mode': 'Markdown'
            }
            response = await client.post(url, data=data)

        if response.status_code != 200:
            logger.error(f"Telegram API error: {response.text}")
        return response.status_code == 200


async def main():
    logger.info("Starting...")

    # Initialize Telethon for reading channels
    tg_client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await tg_client.start()

    try:
        # Send start message via bot
        await send_telegram_message(
            "🔍 *Анализ новостей о качестве воздуха*\n\nИщу релевантные новости за последние 48 часов..."
        )

        agent = get_agent()
        relevant_count = 0
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

                    # Analyze
                    try:
                        analysis = agent.is_air_quality_news(text)

                        if analysis.get('is_air_quality_news') and analysis.get('confidence', 0) >= MIN_CONFIDENCE:
                            logger.info(f"Found relevant post in {channel}")

                            # Rephrase
                            rephrased = agent.rephrase_news(text)

                            # Format message
                            msg_text = (
                                f"📰 *Новость #{relevant_count + 1}*\n"
                                f"📢 Источник: {channel}\n"
                                f"📊 Уверенность: {analysis.get('confidence', 0):.0%}\n\n"
                                f"*Текст для публикации:*\n{rephrased or text[:500]}\n\n"
                                f"---\n"
                                f"_Оригинал:_ {text[:200]}..."
                            )

                            # Send via bot
                            if message.photo:
                                # Download photo first
                                photo_path = f"./media/temp_{message.id}.jpg"
                                await message.download_media(file=photo_path)
                                await send_telegram_message(msg_text, photo_path)
                                # Clean up
                                os.remove(photo_path)
                            else:
                                await send_telegram_message(msg_text)

                            relevant_count += 1
                            await asyncio.sleep(2)

                    except Exception as e:
                        logger.error(f"Analysis error: {e}")
                        continue

            except Exception as e:
                logger.error(f"Channel {channel} error: {e}")
                continue

        # Final message via bot
        await send_telegram_message(
            f"✅ *Анализ завершён!*\n\n"
            f"• Найдено релевантных новостей: {relevant_count}\n"
            f"• Проверено каналов: {len(CHANNELS_TO_MONITOR)}\n\n"
            f"Хотите опубликовать какую-то из них в @musaffo_news?"
        )

        logger.info(f"Done! Sent {relevant_count} news via bot")

    finally:
        await tg_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
