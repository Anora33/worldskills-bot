# -*- coding: utf-8 -*-
import asyncio
import logging
import os
import sys
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from flask import Flask
import threading

# Load .env (lokal uchun)
load_dotenv()

# Flask app
app = Flask(__name__)

@app.route('/')
def health():
    return "WorldSkills Bot is running!", 200

@app.route('/health')
def health_check():
    return {"status": "ok", "bot": "WorldSkills Professional Bot"}, 200

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# Environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite+aiosqlite:///worldskills.db')
ADMIN_ID = int(os.environ.get('ADMIN_ID', 0))
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
WEBAPP_URL = os.environ.get('WEBAPP_URL', 'https://worldskills-webapp.vercel.app').strip()

if not BOT_TOKEN:
    logging.error("❌ BOT_TOKEN not found!")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# 🎯 Import handlers
try:
    from bot.handlers import start, webapp, admin, ai_chat
    
    dp.include_router(ai_chat.router)  # AI birinchi!
    dp.include_router(start.router)
    dp.include_router(webapp.router)
    dp.include_router(admin.router)
    
    logging.info("✅ Barcha handlerlar yuklandi!")
    logging.info(f"  - start: {hasattr(start, 'router')}")
    logging.info(f"  - webapp: {hasattr(webapp, 'router')}")
    logging.info(f"  - admin: {hasattr(admin, 'router')}")
    logging.info(f"  - ai_chat: {hasattr(ai_chat, 'router')}")
    
except Exception as e:
    logging.error(f"❌ Handler import xatosi: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

async def main():
    logging.info("=" * 50)
    logging.info("✅ WorldSkills Professional Bot ishga tushdi!")
    logging.info(f"🤖 Bot: @{(await bot.get_me()).username}")
    logging.info(f"🌐 Flask: port {os.environ.get('PORT', 5000)}")
    logging.info(f"💾 Database: {DATABASE_URL}")
    logging.info(f"👤 Admin: {ADMIN_ID}")
    logging.info("=" * 50)
    
    # Flask thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot to'xtatildi")
    except Exception as e:
        logging.error(f"❌ Fatal xato: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

