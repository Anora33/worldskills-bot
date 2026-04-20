# -*- coding: utf-8 -*-
"""WorldSkills Bot - Main Entry Point (FIXED VERSION)"""
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
DATABASE_PATH = os.getenv("DATABASE_URL", "worldskills.db").strip()

# ============= 3. LOGGING =============
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ============= 4. UPLOAD FOLDER =============
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, "documents"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, "portfolio"), exist_ok=True)

# ============= 5. DATABASE PATH (FIX: ensure directory exists) =============
# Render'da database fayli yoziladigan papka mavjud bo'lishi kerak
DB_DIR = os.path.dirname(os.path.abspath(DATABASE_PATH)) if os.path.dirname(os.path.abspath(DATABASE_PATH)) else "."
if DB_DIR and not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR, exist_ok=True)

# ============= 6. DATABASE INIT =============
def init_db():
    """SQLite database'ni initialize qilish"""
    try:
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
        
        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id TEXT,
                doc_id TEXT,
                filename TEXT,
                status TEXT DEFAULT 'pending',
                score INTEGER DEFAULT 0,
                comment TEXT,
                uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
            )
        """)
        
        # Portfolio table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id TEXT,
                profession_id TEXT,
                filename TEXT,
                score INTEGER DEFAULT 0,
                comment TEXT,
                uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Database initialized: {DATABASE_PATH}")
        return True
    except Exception as e:
        logger.error(f"❌ Database init error: {e}")
        return False

# Initialize DB
init_db()

# ============= 7. FLASK APP (INIT BEFORE ROUTES!) =============
app = Flask(__name__)
# ✅ FIX: 024 emas, 1024! (25 MB = 25 * 1024 * 1024 bytes)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

# ============= 8. BOT INIT =============
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ============= 9. DATABASE HELPERS =============
def get_user(tid):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (str(tid),))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"get_user error: {e}")
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
        logger.info(f"✅ User added: {tid}")
        return True
    except Exception as e:
        logger.error(f"add_user error: {e}")
        return False

def get_all_users():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY registered_at DESC")
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users
    except Exception as e:
        logger.error(f"get_all_users error: {e}")
        return []

# ============= 10. ADMIN NOTIFICATION =============
async def send_admin_notification(message_text: str):
    try:
        if ADMIN_ID and ADMIN_ID > 0:
            await bot.send_message(chat_id=ADMIN_ID, text=message_text, parse_mode="HTML")
            logger.info(f"✅ Admin notified: {ADMIN_ID}")
    except Exception as e:
        logger.error(f"❌ Admin notification error: {e}")

# ============= 11. FLASK ROUTES (ALL HERE - BEFORE RUN!) =============

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "bot": "WorldSkills Bot"})

@app.route("/")
def index():
    return send_from_directory("web_app", "index.html")

@app.route("/admin-panel")
def admin_panel_page():
    return send_from_directory("web_app", "admin.html")

# Admin auth
def check_admin_auth(req):
    auth = req.headers.get('Authorization', '')
    if not auth.startswith('Bearer '): return False
    return auth.split(' ')[1] == ADMIN_TOKEN

@app.route("/api/admin/stats", methods=["GET"])
def admin_stats():
    if not check_admin_auth(request): return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"total": 10, "approved": 5, "pending": 3, "rejected": 2})

@app.route("/api/admin/documents", methods=["GET"])
def admin_documents():
    if not check_admin_auth(request): return jsonify({"error": "Unauthorized"}), 401
    return jsonify([])

@app.route("/api/admin/portfolio", methods=["GET"])
def admin_portfolio():
    if not check_admin_auth(request): return jsonify({"error": "Unauthorized"}), 401
    return jsonify([])

@app.route("/api/admin/users", methods=["GET"])
def admin_users():
    if not check_admin_auth(request): return jsonify({"error": "Unauthorized"}), 401
    return jsonify(get_all_users())

@app.route("/api/admin/files/<path:filename>", methods=["GET"])
def admin_download_file(filename):
    if not check_admin_auth(request): return jsonify({"error": "Unauthorized"}), 401
    # Search in both documents and portfolio folders
    for folder in ["documents", "portfolio"]:
        filepath = os.path.join(UPLOAD_FOLDER, folder, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

@app.route("/api/documents/upload", methods=["POST"])
def upload_document():
    try:
        tid = request.form.get("telegramId")
        doc_id = request.form.get("docId")
        if "file" not in request.files: return jsonify({"success": False, "error": "No file"}), 400
        file = request.files["file"]
        if file.filename == "" or not file.filename.endswith(".pdf"): return jsonify({"success": False, "error": "Invalid file"}), 400
        if file.content_length > 10 * 1024 * 1024: return jsonify({"success": False, "error": "File too large"}), 400
        
        filename = secure_filename(f"{tid}_{doc_id}_{uuid.uuid4().hex}.pdf")
        filepath = os.path.join(UPLOAD_FOLDER, "documents", str(tid))
        os.makedirs(filepath, exist_ok=True)
        file.save(os.path.join(filepath, filename))
        
        user = get_user(tid)
        notification = f"📄 <b>Yangi hujjat!</b>\n👤 {user.get('fullname') if user else 'N/A'}\n📎 {filename}"
        asyncio.run(send_admin_notification(notification))
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Document upload error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/portfolio/upload", methods=["POST"])
def upload_portfolio():
    try:
        tid = request.form.get("telegramId")
        prof_id = request.form.get("professionId")
        if "file" not in request.files: return jsonify({"success": False, "error": "No file"}), 400
        file = request.files["file"]
        if file.filename == "" or not file.filename.endswith(".pdf"): return jsonify({"success": False, "error": "Invalid file"}), 400
        if file.content_length > 20 * 1024 * 1024: return jsonify({"success": False, "error": "File too large"}), 400
        
        filename = secure_filename(f"{tid}_{prof_id}_{uuid.uuid4().hex}.pdf")
        filepath = os.path.join(UPLOAD_FOLDER, "portfolio", str(tid), prof_id)
        os.makedirs(filepath, exist_ok=True)
        file.save(os.path.join(filepath, filename))
        
        user = get_user(tid)
        notification = f"💼 <b>Yangi portfolio!</b>\n👤 {user.get('fullname') if user else 'N/A'}\n📎 {filename}"
        asyncio.run(send_admin_notification(notification))
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Portfolio upload error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/admin/review/document", methods=["POST"])
def admin_review_document():
    if not check_admin_auth(request): return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"success": True, "message": "Reviewed"})

@app.route("/api/admin/review/portfolio", methods=["POST"])
def admin_review_portfolio():
    if not check_admin_auth(request): return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"success": True, "message": "Scored"})

# ============= 12. IMPORT HANDLERS (AFTER bot/dp INIT) =============
try:
    from bot.handlers import start, ai_chat, webapp
    dp.include_router(start.router)
    dp.include_router(ai_chat.router)
    dp.include_router(webapp.router)
    logger.info("✅ All handlers loaded!")
except Exception as e:
    logger.error(f"❌ Error loading handlers: {e}")

# ============= 13. MAIN EXECUTION =============
def run_flask():
    """Flask'ni alohida thread'da ishga tushirish"""
    app.run(host="0.0.0.0", port=5000, threaded=True)

if __name__ == "__main__":
    logger.info("✅ WorldSkills Bot started! @worldskills_uzbekistan_bot")
    
    # Flask'ni background thread'da ishga tushirish
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("✅ Flask started on port 5000")
    
    # Aiogram polling (main thread)
    try:
        asyncio.run(dp.start_polling(bot))
    except Exception as e:
        logger.error(f"❌ Polling error: {e}")
