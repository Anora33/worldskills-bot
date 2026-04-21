# -*- coding: utf-8 -*-
"""WorldSkills Bot - FINAL VERSION with PDF Upload"""
import os, logging, asyncio, threading, sqlite3, uuid
from flask import Flask, request, jsonify, send_from_directory, send_file
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
os.makedirs(os.path.join(UPLOAD_DIR, "documents"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "portfolio"), exist_ok=True)

# 5. Database init
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            telegram_id TEXT PRIMARY KEY, fullname TEXT, phone TEXT, 
            profession_en TEXT, profession_uz TEXT, status TEXT DEFAULT 'pending',
            registered_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT, doc_type TEXT, filename TEXT,
            status TEXT DEFAULT 'pending', score INTEGER DEFAULT 0,
            comment TEXT, uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT, profession_id TEXT, filename TEXT,
            status TEXT DEFAULT 'pending', score INTEGER DEFAULT 0,
            comment TEXT, uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
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

def add_document(tid, doc_type, filename):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO documents (telegram_id, doc_type, filename) VALUES (?,?,?)",
                 (str(tid), doc_type, filename))
        conn.commit()
        conn.close()
        return True
    except: return False

def add_portfolio(tid, prof_id, filename):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO portfolio (telegram_id, profession_id, filename) VALUES (?,?,?)",
                 (str(tid), prof_id, filename))
        conn.commit()
        conn.close()
        return True
    except: return False

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

@app.route("/admin-panel")
def admin_panel():
    return send_from_directory(WEBAPP_DIR, "admin.html")

# Admin auth
def check_admin_auth(req):
    auth = req.headers.get('Authorization', '')
    if not auth.startswith('Bearer '): return False
    return auth.split(' ')[1] == os.getenv('ADMIN_TOKEN', 'secret123')

# Document upload
@app.route("/api/documents/upload", methods=["POST"])
def upload_document():
    try:
        tid = request.form.get("telegramId")
        doc_id = request.form.get("docId")
        file = request.files.get("file")
        
        if not file or not file.filename.endswith(".pdf"):
            return jsonify({"success": False, "error": "Faqat PDF fayllar"}), 400
        
        if file.size > 10 * 1024 * 1024:
            return jsonify({"success": False, "error": "Max 10 MB"}), 400
        
        filename = secure_filename(f"{tid}_{doc_id}_{uuid.uuid4().hex}.pdf")
        filepath = os.path.join(UPLOAD_DIR, "documents", str(tid))
        os.makedirs(filepath, exist_ok=True)
        file.save(os.path.join(filepath, filename))
        
        add_document(tid, doc_id, filename)
        
        user = get_user(tid)
        asyncio.run(notify_admin(
            f"📄 <b>Yangi hujjat!</b>\n"
            f"👤 {user.get('fullname') if user else 'N/A'}\n"
            f"📎 {filename}"
        ))
        
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Portfolio upload
@app.route("/api/portfolio/upload", methods=["POST"])
def upload_portfolio():
    try:
        tid = request.form.get("telegramId")
        prof_id = request.form.get("professionId")
        file = request.files.get("file")
        
        if not file or not file.filename.endswith(".pdf"):
            return jsonify({"success": False, "error": "Faqat PDF fayllar"}), 400
        
        if file.size > 20 * 1024 * 1024:
            return jsonify({"success": False, "error": "Max 20 MB"}), 400
        
        filename = secure_filename(f"{tid}_{prof_id}_{uuid.uuid4().hex}.pdf")
        filepath = os.path.join(UPLOAD_DIR, "portfolio", str(tid), prof_id)
        os.makedirs(filepath, exist_ok=True)
        file.save(os.path.join(filepath, filename))
        
        add_portfolio(tid, prof_id, filename)
        
        user = get_user(tid)
        asyncio.run(notify_admin(
            f"💼 <b>Yangi portfolio!</b>\n"
            f"👤 {user.get('fullname') if user else 'N/A'}\n"
            f"📎 {filename}"
        ))
        
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Portfolio error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Admin review endpoints
@app.route("/api/admin/review/document", methods=["POST"])
def admin_review_document():
    if not check_admin_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    doc_id = data.get("docId")
    action = data.get("action")  # approved/rejected
    score = data.get("score", 0)
    comment = data.get("comment", "")
    
    # Update database
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE documents SET status=?, score=?, comment=? WHERE id=?",
                 (action, score, comment, doc_id))
        conn.commit()
        conn.close()
        
        # Notify user
        tid = data.get("telegramId")
        user = get_user(tid)
        if action == "approved":
            msg = f"✅ <b>Hujjatingiz tasdiqlandi!</b>\n⭐ Ball: {score}/100"
        else:
            msg = f"❌ <b>Hujjatingiz rad etildi</b>\n💬 Sabab: {comment}"
        asyncio.run(notify_admin(msg))
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/admin/review/portfolio", methods=["POST"])
def admin_review_portfolio():
    if not check_admin_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    portfolio_id = data.get("portfolioId")
    action = data.get("action")
    score = data.get("score", 0)
    comment = data.get("comment", "")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE portfolio SET status=?, score=?, comment=? WHERE id=?",
                 (action, score, comment, portfolio_id))
        conn.commit()
        conn.close()
        
        tid = data.get("telegramId")
        user = get_user(tid)
        if action == "approved":
            msg = f"⭐ <b>Ishingiz baholandi!</b>\n🏆 Ball: {score}/100"
        else:
            msg = f"❌ <b>Ishingiz rad etildi</b>\n💬 Sabab: {comment}"
        asyncio.run(notify_admin(msg))
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 10. Import Handlers
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
