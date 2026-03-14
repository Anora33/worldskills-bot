# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Start command with keyboard"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📱 Mini App", web_app=WebAppInfo(url="https://worldskills-webapp.vercel.app"))
    builder.button(text="📊 Statistika", callback_data="stats")
    builder.button(text="🤖 Yordam", callback_data="help")
    builder.adjust(1)
    
    await message.answer(
        "🏆 <b>WorldSkills Professional Bot</b>\n\n"
        "Xush kelibsiz!\n\n"
        "📱 Mini App orqali ro'yxatdan o'ting\n"
        "📊 Statistika va natijalaringizni ko'ring\n"
        "🤖 Yordam uchun /help\n\n"
        "<i>Mini App tugmasini bosing!</i>",
        reply_markup=builder.as_markup()
    )

@router.message(Command("app"))
async def cmd_app(message: Message):
    """Mini App command"""
    await message.answer(
        "📱 <b>Mini App</b>\n\n"
        "Quyidagi tugmani bosing:",
        reply_markup=InlineKeyboardBuilder().button(
            text="🚀 Mini Appni Ochish", 
            web_app=WebAppInfo(url="https://worldskills-webapp.vercel.app")
        ).as_markup()
    )

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Statistics command"""
    await message.answer(
        "📊 <b>Statistika</b>\n\n"
        "👤 Foydalanuvchilar: 0\n"
        "📝 Topshiriqlar: 0\n"
        "🏆 Natijalar: 0\n\n"
        "<i>Tez orada ma'lumotlar ko'rsatiladi...</i>"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Help command"""
    await message.answer(
        "🤖 <b>Yordam</b>\n\n"
        "<b>Mavjud buyruqlar:</b>\n"
        "/start - Botni ishga tushirish\n"
        "/app - Mini Appni ochish\n"
        "/stats - Statistikani ko'rish\n"
        "/help - Yordam\n\n"
        "<b>Savol bo'lsa:</b> @admin ga yozing"
    )
