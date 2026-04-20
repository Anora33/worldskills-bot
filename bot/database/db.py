# -*- coding: utf-8 -*-
import sqlite3, logging, os
from datetime import datetime

logger = logging.getLogger(__name__)
DATABASE_PATH = os.getenv("DATABASE_URL", "worldskills.db")

def init_db():
    """Database va jadvallarni yaratish"""
    conn = sqlite3.connect(DATABASE_PATH)
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
    logger.info(f"✅ Database initialized: {DATABASE_PATH}")

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

# Initialize on import
init_db()
