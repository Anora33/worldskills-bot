# -*- coding: utf-8 -*-
import os

# Render uchun: os.environ.get() ishlatamiz (load_dotenv shart emas)

# Bot token
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Database URL
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite+aiosqlite:///worldskills.db')

# Admin ID
ADMIN_ID = int(os.environ.get('ADMIN_ID', 0))

# Groq API Key
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

# Secret key
SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key-change-in-production')

# Vercel URL (Mini App) - bo'sh joylarsiz!
WEBAPP_URL = os.environ.get('WEBAPP_URL', 'https://worldskills-webapp.vercel.app').strip()

# Tekshirish
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables!")
if not GROQ_API_KEY:
    print("⚠️ Warning: GROQ_API_KEY not set, AI features may not work")
