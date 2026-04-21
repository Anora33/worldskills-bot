# -*- coding: utf-8 -*-
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("admin"))
async def admin_help(message: Message):
    """Admin yordami - kontakt ma'lumotlari"""
    
    # Inline keyboard - Telegram linklar
    builder = InlineKeyboardBuilder()
    builder.button(text="📱 Telegram", url="https://t.me/worldskills_admin")
    builder.button(text=" Telefon", url="tel:+998933404080")
    builder.button(text="📧 Email", url="mailto:dadaxon45@gmail.com")
    builder.button(text="🌐 Web-sayt", url="https://worldskills.uz/ru")
    builder.button(text="📘 Facebook", url="https://www.facebook.com/WorldskillsUzbekistan/")
    builder.button(text="📱 Telegram Kanal", url="https://t.me/worldskillstalim")
    builder.button(text="🎬 YouTube", url="https://www.youtube.com/@worldskillsuzbekistan3441")
    builder.button(text="📷 Instagram", url="https://www.instagram.com/worldskillsuzbekistan/")
    builder.adjust(2)
    
    await message.answer(
        "👨‍💼 <b>Admin Yordami</b>\n\n"
        "📞 <b>Aloqa:</b>\n"
        "• Telegram: @worldskills_admin\n"
        "• Telefon: +998 93 340 40 80\n"
        "• Email: dadaxon45@gmail.com\n\n"
        "🌐 <b>Ijtimoiy tarmoqlar:</b>\n"
        "• Web-sayt: worldskills.uz\n"
        "• Facebook: Worldskills Uzbekistan\n"
        "• Telegram: @worldskillstalim\n"
        "• YouTube: WorldSkills Uzbekistan\n"
        "• Instagram: @worldskillsuzbekistan\n\n"
        "<i>Savollaringiz bo'lsa, bemalol murojaat qiling!</i>",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    
    logger.info(f"✅ Admin help sent to {message.from_user.id}")

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Yordam menyusi"""
    builder = InlineKeyboardBuilder()
    builder.button(text="👨‍💼 Admin yordami", callback_data="admin_help")
    builder.button(text="📱 Mini App", callback_data="mini_app")
    builder.adjust(1)
    
    await message.answer(
        "📚 <b>Yordam</b>\n\n"
        "🤖 <b>Botdan qanday foydalanish:</b>\n"
        "1️⃣ /start - Ro'yxatdan o'tish\n"
        "2️⃣ Mini App - Kasb tanlash va hujjat yuklash\n"
        "3️⃣ /admin - Admin bilan bog'lanish\n"
        "4️⃣ /help - Bu yordam menyusi\n\n"
        "<i>Qanday yordam kerak?</i>",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "admin_help")
async def callback_admin_help(callback: types.CallbackQuery):
    await callback.answer()
    await admin_help(callback.message)
