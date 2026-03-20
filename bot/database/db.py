# -*- coding: utf-8 -*-
import sqlite3, logging, os
from bot.config import DATABASE_URL

logger = logging.getLogger(__name__)

def get_db_path():
    """Render va lokal uchun to'g'ri database path"""
    # Agar DATABASE_URL fayl path'i bo'lsa
    if DATABASE_URL and not DATABASE_URL.startswith("postgresql"):
        # Render uchun writable path
        if os.environ.get("RENDER"):
            return "/opt/render/project/src/worldskills.db"
        # Lokal uchun
        return DATABASE_URL if DATABASE_URL else "worldskills.db"
    # PostgreSQL uchun (kelajakda)
    return DATABASE_URL

def init_db():
    db_path = get_db_path()
    logger.info(f"🗄️ Database path: {db_path}")
    
    try:
        # Directory mavjudligini tekshirish
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"📁 Created directory: {db_dir}")
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            fullname TEXT NOT NULL,
            phone TEXT NOT NULL,
            profession TEXT NOT NULL,
            language TEXT DEFAULT 'uz',
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'approved',
            admin_score INTEGER DEFAULT 0,
            admin_comment TEXT)''')
        
        # Admin logs table
        c.execute('''CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            admin_id INTEGER,
            action TEXT,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Database init error: {e}")
        logger.error(f"❌ Current directory: {os.getcwd()}")
        logger.error(f"❌ Directory permissions: {os.access(os.getcwd(), os.W_OK)}")
        return False

def get_user(tid):
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        r = conn.execute("SELECT * FROM users WHERE telegram_id=?", (tid,)).fetchone()
        conn.close()
        return {k: r[k] for k in r.keys()} if r else None
    except Exception as e:
        logger.error(f"❌ get_user error: {e}")
        return None

def add_user(tid, fn, ph, prof, lang='uz'):
    try:
        conn = sqlite3.connect(get_db_path())
        conn.execute("INSERT OR REPLACE INTO users (telegram_id,fullname,phone,profession,language,status) VALUES (?,?,?,?,?,'approved')",(tid,fn,ph,prof,lang))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ add_user error: {e}")
        return False

def update_user_status(tid, status, score=0):
    try:
        conn = sqlite3.connect(get_db_path())
        conn.execute("UPDATE users SET status=?, admin_score=? WHERE telegram_id=?",(status,score,tid))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ update_user_status error: {e}")
        return False

def get_all_users():
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        users = [{k:r[k] for k in r.keys()} for r in conn.execute("SELECT * FROM users ORDER BY registered_at DESC").fetchall()]
        conn.close()
        return users
    except Exception as e:
        logger.error(f"❌ get_all_users error: {e}")
        return []

def add_log(uid, aid, act, cmt=""):
    try:
        conn = sqlite3.connect(get_db_path())
        conn.execute("INSERT INTO admin_logs (user_id,admin_id,action,comment) VALUES (?,?,?,?)",(uid,aid,act,cmt))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ add_log error: {e}")
        return False
