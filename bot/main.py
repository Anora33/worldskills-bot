# -*- coding: utf-8 -*-
import os, sys, logging, asyncio, uuid
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

# Load environment variables FIRST
load_dotenv()

# ============= CONFIG =============
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "secret123")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://worldskills-bot.onrender.com").strip()
DATABASE_PATH = os.getenv("DATABASE_URL", "worldskills.db").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

# ============= UPLOAD CONFIG =============
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, "documents"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, "portfolio"), exist_ok=True)

# ============= LOGGING =============
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ============= FLASK APP (INIT FIRST!) =============
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB max

# ============= BOT INIT =============
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ============= IMPORT HANDLERS (AFTER bot/dp INIT) =============
from bot.handlers import start, ai_chat, webapp  # admin handler temporarily removed

# ============= REGISTER HANDLERS =============
dp.include_router(start.router)
dp.include_router(ai_chat.router)
dp.include_router(webapp.router)
# dp.include_router(admin.router)  # Temporarily disabled

# ============= DATABASE FUNCTIONS =============
# (Your existing db functions here...)

def get_user(tid):
    """Placeholder - replace with actual DB query"""
    return {"fullname": "Test User", "phone": "+998901234567", "profession": "Test Profession"}

def get_all_users():
    """Placeholder"""
    return []

# ============= ADMIN NOTIFICATION =============
async def send_admin_notification(message_text: str):
    """Admin'ga xabar yuborish"""
    try:
        if ADMIN_ID and ADMIN_ID > 0:
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=message_text,
                parse_mode="HTML"
            )
            logger.info(f"✅ Admin notified: {ADMIN_ID}")
    except Exception as e:
        logger.error(f"❌ Admin notification error: {e}")

# ============= FLASK ROUTES (ALL BEFORE app.run!) =============

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "bot": "WorldSkills Bot"})

@app.route("/")
def index():
    return send_from_directory("web_app", "index.html")

@app.route("/admin-panel")
def admin_panel_page():
    return send_from_directory("web_app", "admin.html")

# Admin auth check
def check_admin_auth(request):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return False
    token = auth_header.split(' ')[1]
    return token == ADMIN_TOKEN

# Admin stats
@app.route("/api/admin/stats", methods=["GET"])
def admin_stats():
    if not check_admin_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"total": 10, "approved": 5, "pending": 3, "rejected": 2})

# Admin documents list
@app.route("/api/admin/documents", methods=["GET"])
def admin_documents():
    if not check_admin_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify([])

# Admin portfolio list
@app.route("/api/admin/portfolio", methods=["GET"])
def admin_portfolio():
    if not check_admin_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify([])

# Admin users list
@app.route("/api/admin/users", methods=["GET"])
def admin_users():
    if not check_admin_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(get_all_users())

# Admin file download
@app.route("/api/admin/files/<filename>", methods=["GET"])
def admin_download_file(filename):
    if not check_admin_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

# Document upload
@app.route("/api/documents/upload", methods=["POST"])
def upload_document():
    try:
        tid = request.form.get("telegramId")
        doc_id = request.form.get("docId")
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file"}), 400
        file = request.files["file"]
        if file.filename == "" or not file.filename.endswith(".pdf"):
            return jsonify({"success": False, "error": "Invalid file"}), 400
        if file.content_length > 10 * 1024 * 1024:
            return jsonify({"success": False, "error": "File too large"}), 400
        
        filename = secure_filename(f"{tid}_{doc_id}_{uuid.uuid4().hex}.pdf")
        filepath = os.path.join(UPLOAD_FOLDER, "documents", str(tid))
        os.makedirs(filepath, exist_ok=True)
        file.save(os.path.join(filepath, filename))
        
        # Admin notification
        user = get_user(tid)
        notification = f"📄 <b>Yangi hujjat!</b>\n👤 {user.get('fullname')}\n📎 {filename}"
        asyncio.run(send_admin_notification(notification))
        
        return jsonify({"success": True, "message": "Uploaded"})
    except Exception as e:
        logger.error(f"Document upload error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Portfolio upload
@app.route("/api/portfolio/upload", methods=["POST"])
def upload_portfolio():
    try:
        tid = request.form.get("telegramId")
        prof_id = request.form.get("professionId")
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file"}), 400
        file = request.files["file"]
        if file.filename == "" or not file.filename.endswith(".pdf"):
            return jsonify({"success": False, "error": "Invalid file"}), 400
        if file.content_length > 20 * 1024 * 1024:
            return jsonify({"success": False, "error": "File too large"}), 400
        
        filename = secure_filename(f"{tid}_{prof_id}_{uuid.uuid4().hex}.pdf")
        filepath = os.path.join(UPLOAD_FOLDER, "portfolio", str(tid), prof_id)
        os.makedirs(filepath, exist_ok=True)
        file.save(os.path.join(filepath, filename))
        
        # Admin notification
        user = get_user(tid)
        notification = f"💼 <b>Yangi portfolio!</b>\n👤 {user.get('fullname')}\n📎 {filename}"
        asyncio.run(send_admin_notification(notification))
        
        return jsonify({"success": True, "message": "Uploaded"})
    except Exception as e:
        logger.error(f"Portfolio upload error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Admin review endpoints (placeholder)
@app.route("/api/admin/review/document", methods=["POST"])
def admin_review_document():
    if not check_admin_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"success": True, "message": "Review completed"})

@app.route("/api/admin/review/portfolio", methods=["POST"])
def admin_review_portfolio():
    if not check_admin_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"success": True, "message": "Scored successfully"})

# ============= MAIN EXECUTION =============
if __name__ == "__main__":
    # Start Flask in background thread
    import threading
    flask_thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=5000, threaded=True),
        daemon=True
    )
    flask_thread.start()
    
    logger.info("✅ WorldSkills Bot started! @worldskills_uzbekistan_bot")
    
    # Start aiogram polling
    asyncio.run(dp.start_polling(bot))
