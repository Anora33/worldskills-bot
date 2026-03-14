# -*- coding: utf-8 -*-
import asyncio
import logging
import os
import sys
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from flask import Flask
import threading

# Load .env file (lokal test uchun!)
load_dotenv()

print("=" * 50)
print("BOT STARTING...")
print("=" * 50)

# Flask
app = Flask(__name__)
@app.route('/')
def health():
    return "OK", 200

@app.route('/health')
def health_check():
    return {"status": "ok", "bot": "WorldSkills"}, 200

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    print(f"Flask running on port {port}")
    app.run(host='0.0.0.0', port=port)

# Check env vars
BOT_TOKEN = os.environ.get('BOT_TOKEN')
print(f"BOT_TOKEN: {'SET' if BOT_TOKEN else 'NOT SET'}")
print(f"ADMIN_ID: {os.environ.get('ADMIN_ID', 'NOT SET')}")
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'NOT SET')}")

if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN is required!")
    sys.exit(1)

print("Creating bot...")
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("✅ Bot is working! /app tugmasini bosing")

async def main():
    print("Starting Flask thread...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    print("Starting polling...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        print("=" * 50)
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
