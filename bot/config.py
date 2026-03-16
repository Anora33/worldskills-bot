# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://worldskills-webapp.vercel.app")
DATABASE_URL = "worldskills.db"

USE_GROQ = bool(GROQ_API_KEY and GROQ_API_KEY.strip())
