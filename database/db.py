# -*- coding: utf-8 -*-
"""
Database - Foydalanuvchilarni SQLite da saqlash
"""
import sqlite3
import logging

logger = logging.getLogger(__name__)
DATABASE_URL = "worldskills.db"

def init_db():
    """Database jadvalini yaratish"""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            fullname TEXT NOT NULL,
            phone TEXT NOT NULL,
            profession TEXT NOT NULL,
            language TEXT DEFAULT 'uz',
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            admin_score INTEGER DEFAULT 0,
            admin_comment TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            admin_id INTEGER,
            action TEXT,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    logger.info("✅ Database initialized")

def get_user(telegram_id: int):
    """Foydalanuvchini topish"""
    try:
        conn = sqlite3.connect(DATABASE_URL)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    except Exception as e:
        logger.error(f"❌ Error in get_user: {e}")
        return None
    finally:
        conn.close()

def add_user(telegram_id: int, fullname: str, phone: str, profession: str, language: str = 'uz'):
    """Yangi foydalanuvchi qo'shish"""
    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (telegram_id, fullname, phone, profession, language)
            VALUES (?, ?, ?, ?, ?)
        ''', (telegram_id, fullname, phone, profession, language))
        conn.commit()
        logger.info(f"✅ User added: {telegram_id}")
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"⚠️ User already exists: {telegram_id}")
        return False
    except Exception as e:
        logger.error(f"❌ Error in add_user: {e}")
        return False
    finally:
        conn.close()

def update_user_status(telegram_id: int, status: str, admin_score: int = None, admin_comment: str = None):
    """Statusni yangilash"""
    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        if admin_score is not None:
            cursor.execute('''
                UPDATE users SET status = ?, admin_score = ?, admin_comment = ?
                WHERE telegram_id = ?
            ''', (status, admin_score, admin_comment, telegram_id))
        else:
            cursor.execute('UPDATE users SET status = ? WHERE telegram_id = ?', (status, telegram_id))
        conn.commit()
        logger.info(f"✅ User {telegram_id} status updated to {status}")
        return True
    except Exception as e:
        logger.error(f"❌ Error in update_user_status: {e}")
        return False
    finally:
        conn.close()

def get_all_users():
    """Barcha foydalanuvchilar"""
    try:
        conn = sqlite3.connect(DATABASE_URL)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY registered_at DESC")
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users
    except Exception as e:
        logger.error(f"❌ Error in get_all_users: {e}")
        return []
    finally:
        conn.close()

def add_admin_log(user_id: int, admin_id: int, action: str, comment: str = ""):
    """Admin log qo'shish"""
    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO admin_logs (user_id, admin_id, action, comment)
            VALUES (?, ?, ?, ?)
        ''', (user_id, admin_id, action, comment))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ Error in add_admin_log: {e}")
        return False
    finally:
        conn.close()