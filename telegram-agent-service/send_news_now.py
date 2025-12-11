"""
Quick script to send found air quality news to user
"""

import os
import asyncio
from datetime import datetime, timedelta
import logging

from dotenv import load_dotenv
load_dotenv()

from telethon import TelegramClient
from telethon.tl.types import Message

from air_quality_agent import get_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_ID = int(os.getenv('TELEGRAM_API_ID', '0'))
API_HASH = os.getenv('TELEGRAM_API_HASH', '')
SESSION_NAME = 'air_quality_bot'
TARGET_USER_ID = 832620295
CHANNELS_TO_MONITOR = ['@kunuzofficial', '@uza_uz', '@Daryo', '@zamonuz']
MIN_CONFIDENCE = 0.6


async def main():
    logger.info("Starting...")

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()

    try:
        user = await client.get_entity(TARGET_USER_ID)
        logger.info(f"Found user: {user.first_name}")

        # Send start message
        await client.send_message(
            user,
            "🔍 **Анализ новостей о качестве воздуха**\n\n"
            "Ищу релевантные новости за последние 48 часов..."
        )

        agent = get_agent()
        relevant_count = 0
        cutoff_time = datetime.now() - timedelta(hours=48)

        for channel in CHANNELS_TO_MONITOR:
            try:
                logger.info(f"Checking {channel}...")

                async for message in client.iter_messages(channel, limit=30):
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

                            # Send immediately
                            msg_text = (
                                f"📰 **Новость #{relevant_count + 1}**\n"
                                f"📢 Источник: {channel}\n"
                                f"📊 Уверенность: {analysis.get('confidence', 0):.0%}\n\n"
                                f"**Текст для публикации:**\n{rephrased or text[:500]}\n\n"
                                f"---\n"
                                f"_Оригинал:_ {text[:300]}..."
                            )

                            if message.photo:
                                await client.send_file(user, message.photo, caption=msg_text[:1024])
                            else:
                                await client.send_message(user, msg_text)

                            relevant_count += 1
                            await asyncio.sleep(2)

                    except Exception as e:
                        logger.error(f"Analysis error: {e}")
                        continue

            except Exception as e:
                logger.error(f"Channel {channel} error: {e}")
                continue

        # Final message
        await client.send_message(
            user,
            f"✅ **Анализ завершён!**\n\n"
            f"• Найдено релевантных новостей: {relevant_count}\n"
            f"• Проверено каналов: {len(CHANNELS_TO_MONITOR)}\n\n"
            f"Хотите опубликовать какую-то из них в @musaffo_news?"
        )

        logger.info(f"Done! Sent {relevant_count} news to user")

    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
