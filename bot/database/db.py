# -*- coding: utf-8 -*-
import sqlite3, logging
from bot.config import DATABASE_URL

logger = logging.getLogger(__name__)

def init_db():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
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
    c.execute('''CREATE TABLE IF NOT EXISTS admin_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        admin_id INTEGER,
        action TEXT,
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()
    logger.info("✅ Database initialized")

def get_user(tid):
    try:
        conn = sqlite3.connect(DATABASE_URL)
        conn.row_factory = sqlite3.Row
        r = conn.execute("SELECT * FROM users WHERE telegram_id=?", (tid,)).fetchone()
        conn.close()
        return {k: r[k] for k in r.keys()} if r else None
    except: return None

def add_user(tid, fn, ph, prof, lang='uz'):
    try:
        conn = sqlite3.connect(DATABASE_URL)
        conn.execute("INSERT OR REPLACE INTO users (telegram_id,fullname,phone,profession,language,status) VALUES (?,?,?,?,?,'approved')",(tid,fn,ph,prof,lang))
        conn.commit()
        conn.close()
        return True
    except: return False

def update_user_status(tid, status, score=0):
    try:
        conn = sqlite3.connect(DATABASE_URL)
        conn.execute("UPDATE users SET status=?, admin_score=? WHERE telegram_id=?",(status,score,tid))
        conn.commit()
        conn.close()
        return True
    except: return False

def get_all_users():
    try:
        conn = sqlite3.connect(DATABASE_URL)
        conn.row_factory = sqlite3.Row
        users = [{k:r[k] for k in r.keys()} for r in conn.execute("SELECT * FROM users ORDER BY registered_at DESC").fetchall()]
        conn.close()
        return users
    except: return []

def add_log(uid, aid, act, cmt=""):
    try:
        conn = sqlite3.connect(DATABASE_URL)
        conn.execute("INSERT INTO admin_logs (user_id,admin_id,action,comment) VALUES (?,?,?,?)",(uid,aid,act,cmt))
        conn.commit()
        conn.close()
        return True
    except: return False
