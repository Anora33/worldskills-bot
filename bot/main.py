# -*- coding: utf-8 -*-
"""WorldSkills Bot - FIXED VERSION"""
import os, sys, logging, asyncio, uuid, threading, sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

# 1. Load environment
load_dotenv()

# 2. Config
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://worldskills-bot.onrender.com").strip()

# 3. Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 4. Paths - Render'da ishlash uchun
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, "documents"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, "portfolio"), exist_ok=True)

# Database - yozish mumkin bo'lgan joy
DB_PATH = os.path.join(BASE_DIR, "worldskills.db")

# 5. Database Init
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            telegram_id TEXT PRIMARY KEY,
            fullname TEXT NOT NULL,
            phone TEXT NOT NULL,
            profession TEXT,
            language TEXT DEFAULT 'uz',
            admin_score INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            registered_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.commit()
        conn.close()
        logger.info(f"✅ Database: {DB_PATH}")
        return True
    except Exception as e:
        logger.error(f"❌ DB error: {e}")
        return False

# 6. Flask App
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # ✅ 1024 (not 024!)

# 7. Bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 8. DB Helpers
def get_user(tid):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (str(tid),))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    except:
        return None

def add_user(tid, fullname, phone, profession, language="uz"):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO users (telegram_id, fullname, phone, profession, language) VALUES (?, ?, ?, ?, ?)",
                      (str(tid), fullname, phone, profession, language))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"add_user error: {e}")
        return False

# 9. Admin Notification
async def notify_admin(text):
    try:
        if ADMIN_ID > 0:
            await bot.send_message(ADMIN_ID, text, parse_mode="HTML")
    except:
        pass

# 10. Flask Routes (ALL BEFORE RUN!)
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/")
def index():
    return send_from_directory("web_app", "index.html")

@app.route("/admin-panel")
def admin_panel():
    return send_from_directory("web_app", "admin.html")

@app.route("/api/documents/upload", methods=["POST"])
def upload_doc():
    try:
        tid = request.form.get("telegramId")
        doc_id = request.form.get("docId")
        file = request.files.get("file")
        if not file or not file.filename.endswith(".pdf"):
            return jsonify({"success": False}), 400
        
        filename = secure_filename(f"{tid}_{doc_id}_{uuid.uuid4().hex}.pdf")
        filepath = os.path.join(UPLOAD_FOLDER, "documents", str(tid))
        os.makedirs(filepath, exist_ok=True)
        file.save(os.path.join(filepath, filename))
        
        user = get_user(tid)
        asyncio.run(notify_admin(f"📄 Yangi hujjat!\n👤 {user.get('fullname') if user else 'N/A'}\n📎 {filename}"))
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"success": False}), 500

@app.route("/api/portfolio/upload", methods=["POST"])
def upload_portfolio():
    try:
        tid = request.form.get("telegramId")
        prof_id = request.form.get("professionId")
        file = request.files.get("file")
        if not file or not file.filename.endswith(".pdf"):
            return jsonify({"success": False}), 400
        
        filename = secure_filename(f"{tid}_{prof_id}_{uuid.uuid4().hex}.pdf")
        filepath = os.path.join(UPLOAD_FOLDER, "portfolio", str(tid), prof_id)
        os.makedirs(filepath, exist_ok=True)
        file.save(os.path.join(filepath, filename))
        
        user = get_user(tid)
        asyncio.run(notify_admin(f"💼 Portfolio!\n👤 {user.get('fullname') if user else 'N/A'}\n📎 {filename}"))
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Portfolio error: {e}")
        return jsonify({"success": False}), 500

# 11. Import Handlers
try:
    from bot.handlers import start, ai_chat, webapp
    dp.include_router(start.router)
    dp.include_router(ai_chat.router)
    dp.include_router(webapp.router)
    logger.info("✅ Handlers loaded!")
except Exception as e:
    logger.error(f"❌ Handler error: {e}")

# 12. Main
if __name__ == "__main__":
    init_db()  # ✅ Database FIRST!
    logger.info("✅ WorldSkills Bot started!")
    
    # Flask background
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, threaded=True), daemon=True).start()
    logger.info("✅ Flask on 5000")
    
    # Bot polling
    asyncio.run(dp.start_polling(bot))
