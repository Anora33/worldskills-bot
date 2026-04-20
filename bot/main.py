# -*- coding: utf-8 -*-
"""WorldSkills Bot - FINAL FIXED VERSION"""
import os, logging, asyncio, threading, sqlite3, uuid
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
WEBAPP_DIR = os.path.join(PROJECT_ROOT, "web_app")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
DB_PATH = os.path.join(BASE_DIR, "worldskills.db")

os.makedirs(WEBAPP_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "documents"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "portfolio"), exist_ok=True)

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            telegram_id TEXT PRIMARY KEY,
            fullname TEXT, phone TEXT, profession TEXT,
            language TEXT DEFAULT 'uz', admin_score INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending', registered_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.commit()
        conn.close()
        logger.info(f"✅ DB: {DB_PATH}")
    except Exception as e:
        logger.error(f"❌ DB: {e}")

app = Flask(__name__, static_folder=WEBAPP_DIR, static_url_path='')
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

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

def add_user(tid, fn, ph, prof, lang="uz"):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO users VALUES(?,?,?,?,?,?,?,?)",
                 (str(tid), fn, ph, prof, lang, 0, "pending", None))
        conn.commit()
        conn.close()
        return True
    except: return False

async def notify_admin(txt):
    try:
        if ADMIN_ID > 0:
            await bot.send_message(ADMIN_ID, txt, parse_mode="HTML")
    except: pass

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/")
def index():
    logger.info(f"📄 Serving from {WEBAPP_DIR}")
    return send_from_directory(WEBAPP_DIR, "index.html")

@app.route("/admin-panel")
def admin_panel():
    return send_from_directory(WEBAPP_DIR, "admin.html")

@app.route("/api/documents/upload", methods=["POST"])
def upload_doc():
    try:
        tid = request.form.get("telegramId")
        doc_id = request.form.get("docId")
        file = request.files.get("file")
        if not file or not file.filename.endswith(".pdf"):
            return jsonify({"success": False}), 400
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
        tid = request.form.get("telegramId")
        prof_id = request.form.get("professionId")
        file = request.files.get("file")
        if not file or not file.filename.endswith(".pdf"):
            return jsonify({"success": False}), 400
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

try:
    from bot.handlers import start, ai_chat, webapp
    dp.include_router(start.router)
    dp.include_router(ai_chat.router)
    dp.include_router(webapp.router)
    logger.info("✅ Handlers loaded!")
except Exception as e:
    logger.error(f"❌ Handler error: {e}")

if __name__ == "__main__":
    init_db()
    logger.info("✅ WorldSkills Bot started!")
    logger.info(f"📂 WEBAPP_DIR: {WEBAPP_DIR}")
    logger.info(f"📂 UPLOAD_DIR: {UPLOAD_DIR}")
    logger.info(f"📂 DB_PATH: {DB_PATH}")
    
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, threaded=True), daemon=True).start()
    logger.info("✅ Flask on port 5000")
    
    asyncio.run(dp.start_polling(bot))
