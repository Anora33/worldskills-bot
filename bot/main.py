# -*- coding: utf-8 -*-
import asyncio
import logging
import os
import sys
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from flask import Flask, jsonify
import threading

# Load .env for local testing
load_dotenv()

# Logging setup - RENDER uchun muhim!
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Flask app for health checks
app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health_check():
    return jsonify({"status": "ok", "bot": "WorldSkills Professional Bot"}), 200

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# Environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite+aiosqlite:///worldskills.db')
ADMIN_ID = int(os.environ.get('ADMIN_ID', 0))
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
WEBAPP_URL = os.environ.get('WEBAPP_URL', 'https://worldskills-webapp.vercel.app').strip()

logger.info(f"🔍 BOT_TOKEN loaded: {'YES' if BOT_TOKEN else 'NO'}")
if BOT_TOKEN:
    logger.info(f"🔍 BOT_TOKEN length: {len(BOT_TOKEN)}, has spaces: {' ' in BOT_TOKEN}")

if not BOT_TOKEN or ' ' in BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not found or contains spaces!")
    sys.exit(1)

# Bot va Dispatcher yaratish
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Handler'larni import qilish
try:
    from bot.handlers import start, webapp, admin, ai_chat
    
    # Router'larni qo'shish (AI birinchi!)
    dp.include_router(ai_chat.router)
    dp.include_router(start.router)
    dp.include_router(webapp.router)
    dp.include_router(admin.router)
    
    logger.info("✅ Barcha handlerlar yuklandi!")
    logger.info(f"  - start: {hasattr(start, 'router')}")
    logger.info(f"  - webapp: {hasattr(webapp, 'router')}")
    logger.info(f"  - admin: {hasattr(admin, 'router')}")
    logger.info(f"  - ai_chat: {hasattr(ai_chat, 'router')}")
    
except Exception as e:
    logger.error(f"❌ Handler import xatosi: {e}", exc_info=True)
    sys.exit(1)

async def main():
    # Webhook'ni o'chirish
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Webhook o'chirildi")
    except Exception as e:
        logger.warning(f"⚠️ Webhook o'chirishda ogohlantirish: {e}")
    
    # Bot ma'lumotlari
    logger.info("=" * 50)
    logger.info("✅ WorldSkills Professional Bot ishga tushdi!")
    
    try:
        me = await bot.get_me()
        logger.info(f"🤖 Bot: @{me.username} (id={me.id})")
    except Exception as e:
        logger.error(f"❌ Bot info olishda xato: {e}")
    
    logger.info(f"🌐 Flask: port {os.environ.get('PORT', 5000)}")
    logger.info(f"💾 Database: {DATABASE_URL}")
    logger.info(f"👤 Admin: {ADMIN_ID}")
    logger.info("=" * 50)
    
    # Flask thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("🌐 Flask server ishga tushdi")
    
    # Polling ni boshlash
    logger.info("🔄 Start polling...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⌨️ Bot to'xtatildi (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Fatal xato: {e}", exc_info=True)
        sys.exit(1)
