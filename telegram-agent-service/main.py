"""
Telegram Agent Service
Monitors Telegram channels for air quality news and reposts to target channel
Uses AWS Bedrock with Bearer Token for AI-powered news detection and rephrasing
"""

import os
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import threading

from dotenv import load_dotenv
load_dotenv()

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from telethon import TelegramClient
from telethon.tl.types import Message
from fastapi import FastAPI
import uvicorn

# Import our AI agent (uses AWS Bedrock Bearer Token)
from air_quality_agent import get_agent

# Import web search agent for fallback when no Telegram news found
from web_search_agent import search_web_for_news

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app for Cloud Run health checks
app = FastAPI(title="Telegram Agent Service")

@app.get("/")
async def root():
    return {"service": "Telegram Agent Service", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Telegram credentials
API_ID = int(os.getenv('TELEGRAM_API_ID', '0'))
API_HASH = os.getenv('TELEGRAM_API_HASH', '')
SESSION_NAME = 'air_quality_bot'

# Channels config
CHANNELS_TO_MONITOR = os.getenv('CHANNELS_TO_MONITOR', '@tashkent_air,@uzb_ecology').split(',')
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL', '@musaffo_news')

# AI Agent confidence threshold
MIN_CONFIDENCE = float(os.getenv('MIN_CONFIDENCE', '0.6'))

# Telethon client - lazy initialization
tg_client = None

def get_tg_client():
    global tg_client
    if tg_client is None:
        if API_ID == 0 or not API_HASH:
            logger.warning("Telegram credentials not set, client disabled")
            return None
        tg_client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    return tg_client

# SQLite for processed posts tracking  
import sqlite3

def init_db():
    """Initialize SQLite database for tracking processed posts"""
    conn = sqlite3.connect('processed_posts.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS processed_posts (
            message_id INTEGER,
            channel TEXT,
            processed_at TIMESTAMP,
            PRIMARY KEY (message_id, channel)
        )
    ''')
    conn.commit()
    conn.close()

def is_post_processed(channel: str, message_id: int) -> bool:
    """Check if post was already processed"""
    conn = sqlite3.connect('processed_posts.db')
    c = conn.cursor()
    c.execute('SELECT 1 FROM processed_posts WHERE channel = ? AND message_id = ?', (channel, message_id))
    result = c.fetchone()
    conn.close()
    return result is not None

def mark_post_processed(channel: str, message_id: int):
    """Mark post as processed"""
    conn = sqlite3.connect('processed_posts.db')
    c = conn.cursor()
    c.execute(
        'INSERT OR IGNORE INTO processed_posts (channel, message_id, processed_at) VALUES (?, ?, ?)',
        (channel, message_id, datetime.now())
    )
    conn.commit()
    conn.close()




async def get_channel_posts(hours_back: int = 3) -> List[Dict[str, Any]]:
    """Get recent posts from monitored channels"""
    posts = []
    cutoff_time = datetime.now() - timedelta(hours=hours_back)

    client = get_tg_client()
    if client is None:
        logger.warning("Telegram client not available")
        return posts

    async with client:
        for channel in CHANNELS_TO_MONITOR:
            channel = channel.strip()
            try:
                logger.info(f"Checking channel: {channel}")
                async for message in client.iter_messages(channel, limit=20):
                    if not isinstance(message, Message):
                        continue
                        
                    if message.date.replace(tzinfo=None) < cutoff_time:
                        break
                    
                    # Check if already processed
                    if is_post_processed(channel, message.id):
                        continue
                    
                    text = message.text or message.message or ""

                    # Skip empty messages
                    if not text or len(text.strip()) < 10:
                        continue

                    post_data = {
                        'channel': channel,
                        'message_id': message.id,
                        'text': text,
                        'date': message.date,
                        'has_photo': message.photo is not None,
                        'photo_path': None
                    }
                    
                    # Download photo if exists  
                    if message.photo:
                        photo_path = f"./media/{channel.replace('@', '')}_{message.id}.jpg"
                        await message.download_media(file=photo_path)
                        post_data['photo_path'] = photo_path
                    
                    posts.append(post_data)
                    logger.info(f"Found relevant post: {channel} #{message.id}")
                    
            except Exception as e:
                logger.error(f"Error fetching from {channel}: {e}")
                continue
    
    return posts


async def analyze_and_rephrase_with_agent(original_text: str) -> str:
    """
    Use AI agent to analyze if text is air quality news and rephrase it
    Returns None if not air quality news or rephrasing failed
    """
    agent = get_agent()

    # This method does both: checking if air quality news AND rephrasing
    rephrased = agent.analyze_and_rephrase(original_text, min_confidence=MIN_CONFIDENCE)

    return rephrased


async def send_to_target_channel(text: str, photo_paths: List[str] = None):
    """Send rephrased post to target channel"""
    client = get_tg_client()
    if client is None:
        logger.warning("Telegram client not available")
        return

    async with client:
        try:
            entity = await client.get_entity(TARGET_CHANNEL)

            if photo_paths and len(photo_paths) > 0:
                await client.send_file(
                    entity,
                    photo_paths,
                    caption=text
                )
            else:
                await client.send_message(entity, text)
                
            logger.info(f"✅ Posted to {TARGET_CHANNEL}")
            
        except Exception as e:
            logger.error(f"Failed to send to target channel: {e}")


async def run_monitoring_cycle():
    """Main monitoring cycle"""
    logger.info("🔄 Starting monitoring cycle...")

    # Get recent posts (24 hours)
    posts = await get_channel_posts(hours_back=24)

    if not posts:
        logger.info("No new air quality posts found in Telegram channels")
        logger.info("🌐 Falling back to web search for news...")

        try:
            # Use web search agent to find news
            web_news = await search_web_for_news()

            if web_news:
                logger.info(f"Found {len(web_news)} news from web search")
                # Convert web news to same format as Telegram posts
                for news in web_news:
                    posts.append({
                        'channel': 'web_search',
                        'message_id': news['id'],
                        'text': f"{news.get('title', '')}\n\n{news.get('text', '')}",
                        'date': datetime.now(),
                        'has_photo': news.get('photo_path') is not None,
                        'photo_path': news.get('photo_path'),
                        'source_url': news.get('source_url', ''),
                        'from_web_search': True
                    })
            else:
                logger.warning("Web search also returned no results")
                return
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return

    logger.info(f"Found {len(posts)} relevant posts")
    
    # Process each post
    for post in posts:
        try:
            logger.info(f"Processing: {post['channel']} #{post['message_id']}")

            # For web search posts, the text is already formatted and verified
            if post.get('from_web_search'):
                rephrased_text = post['text']
                # Add source attribution for web search results
                if post.get('source_url'):
                    rephrased_text += f"\n\nИсточник: {post['source_url']}"
            else:
                # Use AI agent to analyze and rephrase Telegram posts
                # Agent will check if it's air quality news AND rephrase it
                rephrased_text = await analyze_and_rephrase_with_agent(post['text'])

                if not rephrased_text:
                    logger.info(f"Skipping: Not air quality news or low confidence")
                    # Mark as processed even if skipped (to avoid re-checking)
                    mark_post_processed(post['channel'], post['message_id'])
                    continue

            # Send to target channel
            photo_paths = [post['photo_path']] if post['photo_path'] else None
            await send_to_target_channel(rephrased_text, photo_paths)

            # Mark as processed (skip for web search as they have unique IDs)
            if not post.get('from_web_search'):
                mark_post_processed(post['channel'], post['message_id'])

            # Wait between posts to avoid rate limits
            await asyncio.sleep(5)

        except Exception as e:
            logger.error(f"Error processing post: {e}")
            continue
    
    logger.info("✅ Monitoring cycle complete")


def run_monitoring_sync():
    """Wrapper to run async monitoring cycle in sync context"""
    asyncio.run(run_monitoring_cycle())


def start_scheduler():
    """Start the background scheduler"""
    init_db()

    scheduler = BackgroundScheduler(timezone=pytz.UTC)

    # Run every 3 hours
    scheduler.add_job(
        run_monitoring_sync,
        'interval',
        hours=3,
        next_run_time=datetime.now(pytz.UTC)  # Run immediately on start
    )

    scheduler.start()
    logger.info("🚀 Telegram Agent Service started")
    logger.info(f"   Monitoring: {CHANNELS_TO_MONITOR}")
    logger.info(f"   Target: {TARGET_CHANNEL}")
    logger.info(f"   Schedule: Every 3 hours")


def main():
    """Main entry point - runs FastAPI server with background scheduler"""
    # Start scheduler in background
    start_scheduler()

    # Run FastAPI server (required for Cloud Run)
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
