# -*- coding: utf-8 -*-
"""
Database - Foydalanuvchilarni saqlash
"""
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DATABASE_URL = "worldskills.db"


def init_db():
    """Database jadvalini yaratish"""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Foydalanuvchilar jadvali
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS users
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       telegram_id
                       INTEGER
                       UNIQUE
                       NOT
                       NULL,
                       fullname
                       TEXT
                       NOT
                       NULL,
                       phone
                       TEXT
                       NOT
                       NULL,
                       profession
                       TEXT
                       NOT
                       NULL,
                       language
                       TEXT
                       DEFAULT
                       'uz',
                       registered_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       status
                       TEXT
                       DEFAULT
                       'pending',
                       admin_score
                       INTEGER
                       DEFAULT
                       0,
                       admin_comment
                       TEXT
                   )
                   ''')

    # Admin izohlar jadvali
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS admin_logs
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       user_id
                       INTEGER,
                       admin_id
                       INTEGER,
                       action
                       TEXT,
                       comment
                       TEXT,
                       created_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   ''')

    conn.commit()
    conn.close()
    logger.info("✅ Database initialized")


def get_user(telegram_id: int):
    """Foydalanuvchini telegram_id bo'yicha topish"""
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def add_user(telegram_id: int, fullname: str, phone: str, profession: str, language: str = 'uz'):
    """Yangi foydalanuvchi qo'shish"""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    try:
        cursor.execute('''
                       INSERT INTO users (telegram_id, fullname, phone, profession, language)
                       VALUES (?, ?, ?, ?, ?)
                       ''', (telegram_id, fullname, phone, profession, language))
        conn.commit()
        logger.info(f"✅ User added: {telegram_id} - {fullname}")
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"⚠️ User already exists: {telegram_id}")
        return False
    finally:
        conn.close()


def update_user_status(telegram_id: int, status: str, admin_score: int = None, admin_comment: str = None):
    """Admin tomonidan foydalanuvchi statusini yangilash"""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    if admin_score is not None:
        cursor.execute('''
                       UPDATE users
                       SET status        = ?,
                           admin_score   = ?,
                           admin_comment = ?
                       WHERE telegram_id = ?
                       ''', (status, admin_score, admin_comment, telegram_id))
    else:
        cursor.execute('''
                       UPDATE users
                       SET status = ?
                       WHERE telegram_id = ?
                       ''', (status, telegram_id))

    conn.commit()
    conn.close()
    logger.info(f"✅ User {telegram_id} status updated to {status}")


def get_all_users():
    """Barcha foydalanuvchilarni olish"""
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY registered_at DESC")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users


def add_admin_log(user_id: int, admin_id: int, action: str, comment: str = ""):
    """Admin harakatini log qilish"""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('''
                   INSERT INTO admin_logs (user_id, admin_id, action, comment)
                   VALUES (?, ?, ?, ?)
                   ''', (user_id, admin_id, action, comment))
    conn.commit()
    conn.close()