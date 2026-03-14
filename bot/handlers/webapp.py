# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.types import Message
import json
from bot.database.database import async_session
from bot.database.queries import get_user_by_telegram_id, create_user, add_points
from bot.config import config

router = Router()


@router.message(F.web_app_data)
async def process_webapp_data(message: Message):
    """Mini App'dan kelgan ma'lumotlarni qayta ishlash"""
    try:
        data = json.loads(message.web_app_data.data)
        action = data.get('action')
        
        if action == 'register':
            await handle_registration(message, data)
        elif action == 'submit_work':
            await handle_work_submission(message, data)
        else:
            await message.answer("❌ Noma'lum so'rov")
    except json.JSONDecodeError:
        await message.answer("❌ Ma'lumotni qayta ishlashda xato")
    except Exception as e:
        print(f"Error: {e}")
        await message.answer("❌ Xatolik yuz berdi")


async def handle_registration(message: Message,  dict):
    """Ro'yxatdan o'tishni qayta ishlash"""
    telegram_id = data.get('telegramId')
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    phone = data.get('phone')
    competition = data.get('competition')
    
    async with async_session() as db:
        user = await get_user_by_telegram_id(db, telegram_id)
        if user:
            user.full_name = f"{first_name} {last_name}"
            user.competition = competition
            await db.commit()
        else:
            await create_user(
                db=db,
                telegram_id=telegram_id,
                username=message.from_user.username,
                full_name=f"{first_name} {last_name}",
                competition=competition,
                language='uz',
                points=10
            )
    
    await message.answer(
        f"✅ {first_name} {last_name}, ro'yxatdan o'tdingiz!\n\n"
        f"🎯 Yo'nalish: {competition}\n"
        f"🏆 +10 ball qo'shildi!"
    )
    
    # 🎯 ADMINGA XABAR YUBORISH
    admin_id = config.ADMIN_ID
    if admin_id:
        await message.bot.send_message(
            admin_id,
            f"🔔 <b>Yangi Foydalanuvchi!</b>\n\n"
            f"👤 Ism: {first_name} {last_name}\n"
            f"📱 Telefon: {phone}\n"
            f"🎯 Yo'nalish: {competition}\n"
            f"🆔 Telegram ID: <code>{telegram_id}</code>\n"
            f"🏆 Ballar: 10",
            parse_mode="HTML"
        )


async def handle_work_submission(message: Message, data: dict):
    """Ish yuborishni qayta ishlash"""
    telegram_id = data.get('telegramId')
    user_name = data.get('userName')
    competition = data.get('competition')
    work_title = data.get('title')
    work_desc = data.get('description')
    
    await message.answer(
        f"✅ Ish yuborildi!\n\n"
        f"📄 Nomi: {work_title}\n"
        f"📝 Tavsif: {work_desc[:100]}...\n\n"
        f"Admin tekshirgach, baho qo'yadi! 🏆"
    )
    
    async with async_session() as db:
        await add_points(db, telegram_id, 5)
    
    # 🎯 ADMINGA XABAR YUBORISH
    admin_id = config.ADMIN_ID
    if admin_id:
        await message.bot.send_message(
            admin_id,
            f"📸 <b>Yangi Ish Yuborildi!</b>\n\n"
            f"👤 Foydalanuvchi: {user_name}\n"
            f"🎯 Yo'nalish: {competition}\n"
            f"📄 Ish nomi: {work_title}\n"
            f"📝 Tavsif: {work_desc}\n"
            f"🆔 Telegram ID: <code>{telegram_id}</code>\n\n"
            f"<i>Baholash uchun:</i>\n"
            f"<code>/grade {telegram_id} 5</code> (1-5 oralig'ida)",
            parse_mode="HTML"
        )
