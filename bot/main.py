# -*- coding: utf-8 -*-
import logging, asyncio, os, json
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from flask import Flask, request, jsonify
from flask_cors import CORS
from bot.config import BOT_TOKEN, DATABASE_URL, ADMIN_ID, WEBAPP_URL
from bot.database.db import init_db, add_user, update_user_status, get_user as get_db_user
from bot.handlers import start, ai_chat, admin, webapp

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Bot & Dispatcher
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Database init
init_db()
logger.info("✅ Database initialized")

# Flask app
app = Flask(__name__)
CORS(app)

@app.route("/")
def health():
    return "WorldSkills Bot is running! 🚀"

@app.route("/api/register", methods=["POST", "OPTIONS"])
def register():
    logger.info("🔥 /api/register called")
    
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        data = request.json
        logger.info(f"🔥 Registration data: {data}")
        
        tid = data.get("telegramId")
        first_name = data.get("firstName", "")
        last_name = data.get("lastName", "")
        phone = data.get("phone", "")
        profession = data.get("profession", "Dasturlash")
        
        if not all([tid, first_name, phone]):
            logger.error(f"❌ Missing fields: {data}")
            return jsonify({"success": False, "error": "Missing fields"}), 400
        
        fullname = f"{first_name} {last_name}".strip()
        
        # Save to database
        add_user(tid, fullname, phone, profession, "uz")
        update_user_status(tid, "approved", 0)
        logger.info(f"✅ User registered: {tid} - {fullname}")
        
        # Send message to user
        try:
            asyncio.run(bot.send_message(
                tid,
                f"🎉 <b>Muvaffaqiyatli ro'yxatdan o'tdingiz!</b>\n\n"
                f"👤 <b>Ism:</b> {fullname}\n"
                f"🎓 <b>Kompetensiya:</b> {profession}\n"
                f"📱 <b>Telefon:</b> {phone}\n\n"
                f"/start - Bosh menyu",
                parse_mode="HTML"
            ))
            logger.info(f"✅ Message sent to user {tid}")
        except Exception as e:
            logger.error(f"❌ Can't send message to user: {e}")
        
        # Notify admin
        try:
            asyncio.run(bot.send_message(
                ADMIN_ID,
                f"🔔 <b>Yangi ishtirokchi (Mini App)!</b>\n\n"
                f"👤 ID: <code>{tid}</code>\n"
                f"👤 Ism: {fullname}\n"
                f"🎓 Kompetensiya: {profession}\n"
                f"📱 Telefon: {phone}",
                parse_mode="HTML"
            ))
            logger.info(f"✅ Admin notified")
        except Exception as e:
            logger.error(f"❌ Can't notify admin: {e}")
        
        return jsonify({"success": True, "message": "Registered successfully"})
        
    except Exception as e:
        logger.error(f"❌ Registration error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/user/<int:tid>", methods=["GET"])
def get_user_api(tid):
    try:
        user = get_db_user(tid)
        if user:
            return jsonify({"success": True, "registered": True, "user": user})
        return jsonify({"success": True, "registered": False})
    except Exception as e:
        logger.error(f"❌ Get user error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Include routers
dp.include_router(start.router)
dp.include_router(ai_chat.router)
dp.include_router(admin.router)
dp.include_router(webapp.router)
logger.info("✅ All handlers loaded!")

async def main():
    me = await bot.get_me()
    logger.info(f"✅ WorldSkills Bot started! @{me.username}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    async def start_bot_and_flask():
        import threading
        def run_flask():
            port = int(os.environ.get("PORT", 5000))
            app.run(host="0.0.0.0", port=port, threaded=True)
        
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logger.info(f"✅ Flask started on port {os.environ.get('PORT', 5000)}")
        
        await main()
    
    try:
        asyncio.run(start_bot_and_flask())
    except KeyboardInterrupt:
        logger.info("⌨️ Bot stopped")
