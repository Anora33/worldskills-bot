# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

# Doimiy menyu tugmalari (ReplyKeyboard)
def get_main_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📱 Mini App"))
    builder.row(KeyboardButton(text="🌐 English"))
    builder.row(KeyboardButton(text="📝 Registration"))
    builder.row(KeyboardButton(text="📅 Schedule"))
    builder.row(
        KeyboardButton(text="🏆 My competition"),
        KeyboardButton(text="🤖 AI assistant")
    )
    builder.row(
        KeyboardButton(text="⭐ Rating"),
        KeyboardButton(text="📊 My stats")
    )
    return builder.as_markup(resize_keyboard=True)

# Inline tugmalar (bir martalik)
def get_inline_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="📱 Mini App", callback_data="mini_app")
    builder.button(text="📊 Statistika", callback_data="stats")
    builder.button(text="🤖 Yordam", callback_data="help")
    builder.adjust(1)
    return builder.as_markup()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Start command with BOTH keyboards"""
    
    # 1. Doimiy tugmalar (ReplyKeyboard)
    await message.answer(
        "🏆 <b>WorldSkills Professional Bot</b>\n\n"
        "Xush kelibsiz!\n\n"
        "📱 Mini App orqali ro'yxatdan o'ting\n"
        "📊 Statistika va natijalaringizni ko'ring\n"
        "🤖 Yordam uchun /help\n\n"
        "<i>Quyidagi tugmalardan foydalaning:</i>",
        reply_markup=get_main_menu_keyboard()
    )
    
    # 2. Inline tugmalar (qo'shimcha)
    await message.answer(
        "🎯 <b>Tezkor tugmalar:</b>",
        reply_markup=get_inline_menu()
    )

@router.message(Command("app"))
async def cmd_app(message: Message):
    """Mini App command"""
    await message.answer(
        "📱 <b>Mini App</b>\n\n"
        "Mini Appni ochish uchun quyidagi tugmani bosing:",
        reply_markup=InlineKeyboardBuilder().button(
            text="🚀 Mini Appni Ochish",
            web_app=WebAppInfo(url="https://worldskills-webapp.vercel.app")
        ).as_markup()
    )

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Statistics"""
    await message.answer(
        "📊 <b>Statistika</b>\n\n"
        "👤 Foydalanuvchilar: 0\n"
        "📝 Topshiriqlar: 0\n"
        "🏆 Natijalar: 0"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Help command"""
    await message.answer(
        "🤖 <b>Yordam</b>\n\n"
        "<b>Mavjud buyruqlar:</b>\n"
        "/start - Botni ishga tushirish\n"
        "/app - Mini App\n"
        "/stats - Statistika\n"
        "/help - Yordam"
    )

# ========== DOIMIY TUGMALAR HANDLERLARI ==========

@router.message(F.text == "📱 Mini App")
async def handle_mini_app(message: Message):
    await message.answer(
        "📱 <b>Mini App</b>\n\n"
        "Mini Appni ochish uchun quyidagi tugmani bosing:",
        reply_markup=InlineKeyboardBuilder().button(
            text="🚀 Mini Appni Ochish",
            web_app=WebAppInfo(url="https://worldskills-webapp.vercel.app")
        ).as_markup()
    )

@router.message(F.text == "🌐 English")
async def handle_english(message: Message):
    await message.answer("? Language changed: EN")

@router.message(F.text == "📝 Registration")
async def handle_registration(message: Message):
    await message.answer("📝 Registration form coming soon...")

@router.message(F.text == "📅 Schedule")
async def handle_schedule(message: Message):
    await message.answer("📅 Schedule coming soon...")

@router.message(F.text == "🏆 My competition")
async def handle_competition(message: Message):
    await message.answer("🏆 My competition coming soon...")

@router.message(F.text == "🤖 AI assistant")
async def handle_ai(message: Message):
    await message.answer("🤖 AI assistant coming soon...")

@router.message(F.text == "⭐ Rating")
async def handle_rating(message: Message):
    await message.answer("⭐ Rating coming soon...")

@router.message(F.text == "📊 My stats")
async def handle_mystats(message: Message):
    await cmd_stats(message)

# ========== INLINE TUGMALAR HANDLERLARI ==========

@router.callback_query(F.data == "mini_app")
async def callback_mini_app(callback: CallbackQuery):
    await callback.message.answer(
        "📱 <b>Mini App</b>\n\n"
        "Mini Appni ochish uchun quyidagi tugmani bosing:",
        reply_markup=InlineKeyboardBuilder().button(
            text="🚀 Mini Appni Ochish",
            web_app=WebAppInfo(url="https://worldskills-webapp.vercel.app")
        ).as_markup()
    )
    await callback.answer()

@router.callback_query(F.data == "stats")
async def callback_stats(callback: CallbackQuery):
    await cmd_stats(callback.message)
    await callback.answer()

@router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery):
    await cmd_help(callback.message)
    await callback.answer()
