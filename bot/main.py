# -*- coding: utf-8 -*-
"""WorldSkills Bot - Main Entry Point (FIXED)"""
import os, sys, logging, asyncio, uuid, threading, sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, send_file
from werkzeug.utils import secure_filename
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, WebAppInfo, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv

# ============= 1. LOAD ENV =============
load_dotenv()

# ============= 2. CONFIG =============
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "secret123")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://worldskills-bot.onrender.com").strip()

# Database path - Render'da yozish mumkin bo'lgan joy
DB_FILENAME = os.getenv("DATABASE_URL", "worldskills.db").strip()
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_FILENAME)

# ============= 3. LOGGING =============
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ============= 4. UPLOAD FOLDER =============
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, "documents"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, "portfolio"), exist_ok=True)

# ============= 5. DATABASE INIT =============
def init_db():
    """SQLite database'ni initialize qilish"""
    try:
        # Papka mavjudligini tekshirish
        db_dir = os.path.dirname(DATABASE_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id TEXT PRIMARY KEY,
                fullname TEXT NOT NULL,
                phone TEXT NOT NULL,
                profession TEXT,
                language TEXT DEFAULT 'uz',
                admin_score INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                registered_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Database initialized: {DATABASE_PATH}")
        return True
    except Exception as e:
        logger.error(f"❌ Database init error: {e}")
        return False

# ============= 6. FLASK APP (INIT FIRST!) =============
app = Flask(__name__)
# ✅ FIXED: 25 * 1024 * 1024 (not 024!)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB

# ============= 7. BOT INIT =============
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ============= 8. DATABASE HELPERS =============
def get_user(tid):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
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
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO users (telegram_id, fullname, phone, profession, language)
            VALUES (?, ?, ?, ?, ?)
        """, (str(tid), fullname, phone, profession, language))
        conn.commit()
        conn.close()
        return True
    except:
        return False

# ============= 9. ADMIN NOTIFICATION =============
async def send_admin_notification(message_text: str):
    try:
        if ADMIN_ID and ADMIN_ID > 0:
            await bot.send_message(chat_id=ADMIN_ID, text=message_text, parse_mode="HTML")
    except:
        pass

# ============= 10. FLASK ROUTES (ALL HERE - BEFORE RUN!) =============

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

@app.route("/")
def index():
    return send_from_directory("web_app", "index.html")

@app.route("/admin-panel")
def admin_panel_page():
    return send_from_directory("web_app", "admin.html")

def check_admin_auth(req):
    auth = req.headers.get('Authorization', '')
    if not auth.startswith('Bearer '): return False
    return auth.split(' ')[1] == ADMIN_TOKEN

@app.route("/api/admin/stats", methods=["GET"])
def admin_stats():
    if not check_admin_auth(request): return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"total": 10, "approved": 5, "pending": 3, "rejected": 2})

@app.route("/api/documents/upload", methods=["POST"])
def upload_document():
    try:
        tid = request.form.get("telegramId")
        doc_id = request.form.get("docId")
        if "file" not in request.files: return jsonify({"success": False}), 400
        file = request.files["file"]
        if not file.filename.endswith(".pdf"): return jsonify({"success": False}), 400
        
        filename = secure_filename(f"{tid}_{doc_id}_{uuid.uuid4().hex}.pdf")
        filepath = os.path.join(UPLOAD_FOLDER, "documents", str(tid))
        os.makedirs(filepath, exist_ok=True)
        file.save(os.path.join(filepath, filename))
        
        user = get_user(tid)
        asyncio.run(send_admin_notification(f"📄 Yangi hujjat!\n👤 {user.get('fullname') if user else 'N/A'}\n📎 {filename}"))
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"success": False}), 500

@app.route("/api/portfolio/upload", methods=["POST"])
def upload_portfolio():
    try:
        tid = request.form.get("telegramId")
        prof_id = request.form.get("professionId")
        if "file" not in request.files: return jsonify({"success": False}), 400
        file = request.files["file"]
        if not file.filename.endswith(".pdf"): return jsonify({"success": False}), 400
        
        filename = secure_filename(f"{tid}_{prof_id}_{uuid.uuid4().hex}.pdf")
        filepath = os.path.join(UPLOAD_FOLDER, "portfolio", str(tid), prof_id)
        os.makedirs(filepath, exist_ok=True)
        file.save(os.path.join(filepath, filename))
        
        user = get_user(tid)
        asyncio.run(send_admin_notification(f"💼 Yangi portfolio!\n👤 {user.get('fullname') if user else 'N/A'}\n📎 {filename}"))
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Portfolio upload error: {e}")
        return jsonify({"success": False}), 500

# ============= 11. IMPORT HANDLERS =============
try:
    from bot.handlers import start, ai_chat, webapp
    dp.include_router(start.router)
    dp.include_router(ai_chat.router)
    dp.include_router(webapp.router)
    logger.info("✅ Handlers loaded!")
except Exception as e:
    logger.error(f"❌ Handler error: {e}")

# ============= 12. MAIN =============
if __name__ == "__main__":
    # Initialize database FIRST
    init_db()
    
    logger.info("✅ WorldSkills Bot started!")
    
    # Flask in background thread
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, threaded=True), daemon=True).start()
    logger.info("✅ Flask on port 5000")
    
    # Start bot polling
    asyncio.run(dp.start_polling(bot))
