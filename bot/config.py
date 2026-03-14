# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

# .env faylni yuklash
load_dotenv()

# Bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///worldskills.db")

# Admin ID
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# Groq API Key (endi .env dan o'qiladi)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Secret key
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-change-in-production")

# Vercel URL (Mini App)
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://worldskills-webapp.vercel.app")

# Tekshirish
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables!")
if not GROQ_API_KEY:
    print("⚠️ Warning: GROQ_API_KEY not set, AI features may not work")
