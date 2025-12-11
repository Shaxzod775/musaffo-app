"""
Interactive script to authorize Telegram
Run this first to create session
"""

import os
import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv('TELEGRAM_API_ID', '0'))
API_HASH = os.getenv('TELEGRAM_API_HASH', '')
PHONE = os.getenv('PHONE_NUMBER', '')
SESSION_NAME = 'air_quality_bot'

async def authorize():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    print("🔐 Starting Telegram authorization...")
    print(f"📱 Phone: {PHONE}\n")

    await client.start(phone=PHONE)

    if await client.is_user_authorized():
        print("✅ Successfully authorized!")
        print(f"✅ Session saved as: {SESSION_NAME}.session")
        print("\nYou can now run analyze_channels.py")
    else:
        print("❌ Authorization failed")

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(authorize())
