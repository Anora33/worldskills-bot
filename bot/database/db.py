# -*- coding: utf-8 -*-
import sqlite3, logging, os

logger = logging.getLogger(__name__)

def get_db_path():
    """Render'da ishlash uchun to'g'ri path"""
    db_name = os.getenv("DATABASE_URL", "worldskills.db")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), db_name)

def init_db():
    """Database va jadvallarni yaratish"""
    try:
        db_path = get_db_path()
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        conn = sqlite3.connect(db_path)
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
        logger.info(f"✅ DB initialized: {db_path}")
        return True
    except Exception as e:
        logger.error(f"❌ DB init error: {e}")
        return False

def get_user(tid):
    try:
        conn = sqlite3.connect(get_db_path())
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
        conn = sqlite3.connect(get_db_path())
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

# Auto-init on import
init_db()
