"""
One-time script to analyze news and send to user's personal chat
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

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram credentials
API_ID = int(os.getenv('TELEGRAM_API_ID', '0'))
API_HASH = os.getenv('TELEGRAM_API_HASH', '')
SESSION_NAME = 'air_quality_bot'

# User to send news to
TARGET_USER_ID = 832620295

# Channels to monitor
CHANNELS_TO_MONITOR = os.getenv('CHANNELS_TO_MONITOR', '@kunuzofficial,@Ozbekistonn_tyuzbekk_unchamuncha,@uza_uz,@darakchi,@MyGovUz,@toshkent,@Daryo,@zamonuz,@uzauzrus').split(',')

# AI Agent confidence threshold
MIN_CONFIDENCE = float(os.getenv('MIN_CONFIDENCE', '0.6'))


async def get_channel_posts(client, hours_back: int = 24):
    """Get recent posts from monitored channels"""
    posts = []
    cutoff_time = datetime.now() - timedelta(hours=hours_back)

    for channel in CHANNELS_TO_MONITOR:
        channel = channel.strip()
        if not channel:
            continue
        try:
            logger.info(f"Checking channel: {channel}")
            async for message in client.iter_messages(channel, limit=30):
                if not isinstance(message, Message):
                    continue

                if message.date.replace(tzinfo=None) < cutoff_time:
                    break

                text = message.text or message.message or ""

                # Skip empty messages
                if not text or len(text.strip()) < 50:
                    continue

                post_data = {
                    'channel': channel,
                    'message_id': message.id,
                    'text': text,
                    'date': message.date,
                    'has_photo': message.photo is not None,
                    'message': message  # Keep original message for photo
                }

                posts.append(post_data)

        except Exception as e:
            logger.error(f"Error fetching from {channel}: {e}")
            continue

    return posts


def analyze_post(text: str) -> dict:
    """Analyze if post is air quality related and rephrase it"""
    agent = get_agent()

    # First check if it's air quality news
    analysis = agent.is_air_quality_news(text)

    if not analysis.get('is_air_quality_news') or analysis.get('confidence', 0) < MIN_CONFIDENCE:
        return {'is_relevant': False, 'confidence': analysis.get('confidence', 0)}

    # If relevant, rephrase it
    rephrased = agent.rephrase_news(text)

    return {
        'is_relevant': True,
        'confidence': analysis.get('confidence', 0),
        'rephrased_text': rephrased or text,
        'reason': analysis.get('reason', '')
    }


async def main():
    """Main function to analyze and send news"""
    logger.info("Starting news analysis...")

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    async with client:
        # Get user entity
        try:
            user = await client.get_entity(TARGET_USER_ID)
            logger.info(f"Will send news to user: {user.first_name if hasattr(user, 'first_name') else TARGET_USER_ID}")
        except Exception as e:
            logger.error(f"Cannot find user {TARGET_USER_ID}: {e}")
            return

        # Get posts from channels
        posts = await get_channel_posts(client, hours_back=48)
        logger.info(f"Found {len(posts)} posts to analyze")

        if not posts:
            await client.send_message(user, "Не найдено новых постов для анализа за последние 48 часов.")
            return

        # Send intro message
        await client.send_message(
            user,
            f"🔍 **Анализ новостей о качестве воздуха**\n\n"
            f"Найдено {len(posts)} постов из {len(CHANNELS_TO_MONITOR)} каналов.\n"
            f"Анализирую на предмет новостей о воздухе и экологии...\n\n"
            f"⏳ Это может занять несколько минут..."
        )

        relevant_posts = []

        # Analyze each post
        for i, post in enumerate(posts):
            try:
                logger.info(f"Analyzing post {i+1}/{len(posts)} from {post['channel']}")

                result = analyze_post(post['text'])

                if result and result.get('is_relevant'):
                    relevant_posts.append({
                        'channel': post['channel'],
                        'original': post['text'][:500],
                        'rephrased': result.get('rephrased_text', post['text']),
                        'confidence': result.get('confidence', 0),
                        'message': post['message']
                    })
                    logger.info(f"✅ Relevant post found from {post['channel']}")

            except Exception as e:
                logger.error(f"Error analyzing post: {e}")
                continue

        # Send results
        if not relevant_posts:
            await client.send_message(
                user,
                "❌ **Результат анализа**\n\n"
                "Не найдено релевантных новостей о качестве воздуха за последние 48 часов.\n\n"
                "Проверенные каналы:\n" + "\n".join([f"• {ch.strip()}" for ch in CHANNELS_TO_MONITOR])
            )
        else:
            await client.send_message(
                user,
                f"✅ **Найдено {len(relevant_posts)} релевантных новостей!**\n\n"
                f"Отправляю каждую новость отдельным сообщением..."
            )

            for i, post in enumerate(relevant_posts):
                try:
                    # Format message
                    msg = (
                        f"📰 **Новость #{i+1}**\n"
                        f"📢 Источник: {post['channel']}\n"
                        f"📊 Уверенность: {post['confidence']:.0%}\n\n"
                        f"**Переформулированный текст:**\n"
                        f"{post['rephrased']}\n\n"
                        f"---\n"
                        f"_Оригинал (первые 300 символов):_\n"
                        f"{post['original'][:300]}..."
                    )

                    # Try to forward with photo if exists
                    if post['message'].photo:
                        await client.send_file(
                            user,
                            post['message'].photo,
                            caption=msg[:1024]  # Telegram caption limit
                        )
                    else:
                        await client.send_message(user, msg)

                    await asyncio.sleep(1)  # Rate limit

                except Exception as e:
                    logger.error(f"Error sending post {i+1}: {e}")
                    await client.send_message(user, f"Ошибка при отправке новости #{i+1}: {e}")

            # Final summary
            await client.send_message(
                user,
                f"📋 **Итого:**\n\n"
                f"• Проанализировано постов: {len(posts)}\n"
                f"• Релевантных новостей: {len(relevant_posts)}\n"
                f"• Каналов проверено: {len(CHANNELS_TO_MONITOR)}\n\n"
                f"Хотите опубликовать какую-то из этих новостей в @musaffo_news?"
            )

    logger.info("Done!")


if __name__ == "__main__":
    asyncio.run(main())
