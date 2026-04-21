# -*- coding: utf-8 -*-
"""WorldSkills Bot - FINAL CLEAN VERSION"""
import os, logging, asyncio, threading, sqlite3
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

# 1. Load env
load_dotenv()

# 2. Config
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# 3. Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

# 4. Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
WEBAPP_DIR = os.path.join(PROJECT_ROOT, "web_app")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
DB_PATH = os.path.join(BASE_DIR, "worldskills.db")

os.makedirs(WEBAPP_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 5. Database init
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            telegram_id TEXT PRIMARY KEY, fullname TEXT, phone TEXT, 
            profession TEXT, registered_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.commit()
        conn.close()
        logger.info(f"✅ DB: {DB_PATH}")
    except Exception as e:
        logger.error(f"❌ DB: {e}")

# 6. Flask App
app = Flask(__name__, static_folder=WEBAPP_DIR, static_url_path='')
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

# 7. Bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 8. DB Helper
def get_user(tid):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE telegram_id=?", (str(tid),))
        r = c.fetchone()
        conn.close()
        return dict(r) if r else None
    except: return None

async def notify_admin(txt):
    try:
        if ADMIN_ID > 0:
            await bot.send_message(ADMIN_ID, txt, parse_mode="HTML")
    except: pass

# 9. Flask Routes
@app.route("/health")
def health(): return jsonify({"status": "ok"})

@app.route("/")
def index():
    logger.info(f"📄 Serving from {WEBAPP_DIR}")
    return send_from_directory(WEBAPP_DIR, "index.html")

# 10. Import Handlers (AFTER bot/dp init)
try:
    from bot.handlers import start, ai_chat, admin
    dp.include_router(start.router)
    dp.include_router(ai_chat.router)
    dp.include_router(admin.router)
    logger.info("✅ Handlers loaded!")
except Exception as e:
    logger.error(f"❌ Handler error: {e}")

# 11. Main
if __name__ == "__main__":
    init_db()
    logger.info("✅ WorldSkills Bot started!")
    
    # Flask background
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, threaded=True), daemon=True).start()
    logger.info("✅ Flask on port 5000")
    
    # Bot polling
    asyncio.run(dp.start_polling(bot))
