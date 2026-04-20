# -*- coding: utf-8 -*-
"""WorldSkills Bot - FINAL FIXED VERSION"""
import os, logging, asyncio, threading, sqlite3, uuid
from flask import Flask, request, jsonify, send_from_directory, send_file
from werkzeug.utils import secure_filename
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

# 1. Load env FIRST
load_dotenv()

# 2. Config
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "secret123")

# 3. Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

# 4. Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
WEBAPP_DIR = os.path.join(PROJECT_ROOT, "web_app")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
DB_PATH = os.path.join(BASE_DIR, "worldskills.db")

# Create folders
os.makedirs(WEBAPP_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "documents"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "portfolio"), exist_ok=True)

# 5. Database init
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            telegram_id TEXT PRIMARY KEY, fullname TEXT, phone TEXT, profession TEXT,
            language TEXT DEFAULT 'uz', admin_score INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending', registered_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id TEXT, doc_id TEXT,
            filename TEXT, status TEXT DEFAULT 'pending', score INTEGER DEFAULT 0,
            comment TEXT, uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id TEXT, profession_id TEXT,
            filename TEXT, score INTEGER DEFAULT 0, comment TEXT,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.commit()
        conn.close()
        logger.info(f"✅ DB: {DB_PATH}")
    except Exception as e:
        logger.error(f"❌ DB: {e}")

# 6. Flask App (INIT BEFORE ROUTES!)
app = Flask(__name__, static_folder=WEBAPP_DIR, static_url_path='')
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

# 7. Bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 8. DB Helpers
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

def get_all_users():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users ORDER BY registered_at DESC")
        users = [dict(row) for row in c.fetchall()]
        conn.close()
        return users
    except: return []

async def notify_admin(txt):
    try:
        if ADMIN_ID > 0:
            await bot.send_message(ADMIN_ID, txt, parse_mode="HTML")
    except: pass

# ============= ALL FLASK ROUTES HERE (BEFORE RUN!) =============

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/")
def index():
    logger.info(f"📄 Serving from {WEBAPP_DIR}")
    return send_from_directory(WEBAPP_DIR, "index.html")

@app.route("/admin-panel")
def admin_panel_page():
    return send_from_directory(WEBAPP_DIR, "admin.html")

def check_admin_auth(req):
    auth = req.headers.get('Authorization', '')
    if not auth.startswith('Bearer '): return False
    return auth.split(' ')[1] == ADMIN_TOKEN

@app.route("/api/admin/stats", methods=["GET"])
def api_admin_stats():
    if not check_admin_auth(request): return jsonify({"error": "Unauthorized"}), 401
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users"); total = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM documents WHERE status='approved'"); approved = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM documents WHERE status='pending'"); pending = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM documents WHERE status='rejected'"); rejected = c.fetchone()[0]
        conn.close()
        return jsonify({"total": total, "approved": approved, "pending": pending, "rejected": rejected})
    except: return jsonify({"total": 0, "approved": 0, "pending": 0, "rejected": 0})

@app.route("/api/admin/documents", methods=["GET"])
def api_admin_documents():
    if not check_admin_auth(request): return jsonify({"error": "Unauthorized"}), 401
    return jsonify([])

@app.route("/api/admin/portfolio", methods=["GET"])
def api_admin_portfolio():
    if not check_admin_auth(request): return jsonify({"error": "Unauthorized"}), 401
    return jsonify([])

@app.route("/api/admin/users", methods=["GET"])
def api_admin_users():
    if not check_admin_auth(request): return jsonify({"error": "Unauthorized"}), 401
    return jsonify(get_all_users())

@app.route("/api/admin/files/<filename>", methods=["GET"])
def api_admin_files(filename):
    if not check_admin_auth(request): return jsonify({"error": "Unauthorized"}), 401
    filepath = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

@app.route("/api/admin/review/document", methods=["POST"])
def api_admin_review_doc():
    if not check_admin_auth(request): return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    tid = data.get("telegramId"); doc_id = data.get("docId"); action = data.get("action")
    score = data.get("score", 100); comment = data.get("comment", "")
    user = get_user(tid)
    if action == "approved":
        msg = f"✅ <b>Hujjatingiz tasdiqlandi!</b>\n\n⭐ Ball: {score}/100\n💬 {comment or 'Ajoyib!'}"
    else:
        msg = f"❌ <b>Hujjatingiz rad etildi</b>\n\n💬 Sabab: {comment or 'Talablarga javob bermaydi'}\n\n🔄 Qayta yuklang!"
    asyncio.run(notify_admin(msg))
    return jsonify({"success": True})

@app.route("/api/admin/review/portfolio", methods=["POST"])
def api_admin_review_portfolio():
    if not check_admin_auth(request): return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    tid = data.get("telegramId"); action = data.get("action")
    score = data.get("score", 0); comment = data.get("comment", "")
    user = get_user(tid)
    if action == "approved":
        msg = f"⭐ <b>Ishingiz baholandi!</b>\n\n🏆 Ball: {score}/100\n💬 {comment or 'Yaxshi natija!'}"
    else:
        msg = f"❌ <b>Ishingiz rad etildi</b>\n\n💬 Sabab: {comment}\n\n🔄 Qayta yuklang!"
    asyncio.run(notify_admin(msg))
    return jsonify({"success": True})

@app.route("/api/documents/upload", methods=["POST"])
def upload_doc():
    try:
        tid = request.form.get("telegramId"); doc_id = request.form.get("docId")
        file = request.files.get("file")
        if not file or not file.filename.endswith(".pdf"): return jsonify({"success": False}), 400
        fn = secure_filename(f"{tid}_{doc_id}_{uuid.uuid4().hex}.pdf")
        fp = os.path.join(UPLOAD_DIR, "documents", str(tid))
        os.makedirs(fp, exist_ok=True)
        file.save(os.path.join(fp, fn))
        u = get_user(tid)
        asyncio.run(notify_admin(f"📄 Yangi hujjat!\n👤 {u.get('fullname') if u else 'N/A'}\n📎 {fn}"))
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"success": False}), 500

@app.route("/api/portfolio/upload", methods=["POST"])
def upload_portfolio():
    try:
        tid = request.form.get("telegramId"); prof_id = request.form.get("professionId")
        file = request.files.get("file")
        if not file or not file.filename.endswith(".pdf"): return jsonify({"success": False}), 400
        fn = secure_filename(f"{tid}_{prof_id}_{uuid.uuid4().hex}.pdf")
        fp = os.path.join(UPLOAD_DIR, "portfolio", str(tid), prof_id)
        os.makedirs(fp, exist_ok=True)
        file.save(os.path.join(fp, fn))
        u = get_user(tid)
        asyncio.run(notify_admin(f"💼 Portfolio!\n👤 {u.get('fullname') if u else 'N/A'}\n📎 {fn}"))
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Portfolio error: {e}")
        return jsonify({"success": False}), 500

# ============= IMPORT HANDLERS (AFTER bot/dp INIT) =============
try:
    from bot.handlers import start, ai_chat, admin, webapp
    dp.include_router(start.router)
    dp.include_router(ai_chat.router)
    dp.include_router(admin.router)
    dp.include_router(webapp.router)
    logger.info("✅ Handlers loaded!")
except Exception as e:
    logger.error(f"❌ Handler error: {e}")

# ============= MAIN EXECUTION (LAST!) =============
if __name__ == "__main__":
    init_db()
    logger.info("✅ WorldSkills Bot started!")
    logger.info(f"📂 WEBAPP_DIR: {WEBAPP_DIR}")
    
    # Flask in background thread
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, threaded=True), daemon=True).start()
    logger.info("✅ Flask on port 5000")
    
    # Bot polling
    asyncio.run(dp.start_polling(bot))
