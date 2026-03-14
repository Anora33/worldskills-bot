# -*- coding: utf-8 -*-
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from flask import Flask
import threading
import os
from dotenv import load_dotenv

# Environment variables
load_dotenv()

# Flask app (health check uchun)
app = Flask(__name__)

@app.route('/')
def health():
    return "WorldSkills Bot is running! 🤖", 200

@app.route('/health')
def health_check():
    return {"status": "ok", "bot": "WorldSkills Professional Bot"}, 200

# Flask ni alohida thread'da ishga tushirish
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

# Bot sozlamalari
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables!")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Start handler
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "🏆 <b>WorldSkills Professional Bot</b>\n\n"
        "Xush kelibsiz!\n\n"
        "📱 Mini App: /app\n"
        "📊 Statistika: /stats\n"
        "🤖 Yordam: /help"
    )

# Botni ishga tushirish
async def main():
    # Flask ni alohida thread'da ishga tushirish
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    logging.info("✅ WorldSkills Professional Bot ishga tushdi...")
    logging.info("🌐 Flask health server ishga tushdi (port 5000)")
    
    # Bot polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot to'xtatildi")
