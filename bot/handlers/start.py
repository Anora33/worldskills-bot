# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

# Doimiy menyu tugmalari
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

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "🏆 <b>WorldSkills Professional Bot</b>\n\n"
        "Xush kelibsiz!\n\n"
        "📱 Mini App orqali ro'yxatdan o'ting\n"
        "📊 Statistika va natijalaringizni ko'ring\n"
        "🤖 Yordam uchun /help\n\n"
        "<i>Quyidagi tugmalardan foydalaning:</i>",
        reply_markup=get_main_menu_keyboard()
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
    await message.answer("? Language changed: EN\n\nBot language switched to English")

@router.message(F.text == "📝 Registration")
async def handle_registration(message: Message):
    await message.answer(
        "📝 <b>Ro'yxatdan O'tish</b>\n\n"
        "Quyidagi ma'lumotlarni kiriting:\n\n"
        "1️⃣ <b>Ism Familiya:</b>\n"
        "2️⃣ <b>Telefon raqam:</b>\n"
        "3️⃣ <b>WorldSkills yo'nalishi:</b>\n\n"
        "<i>Tez orada to'liq forma qo'shiladi...</i>"
    )

@router.message(F.text == "📅 Schedule")
async def handle_schedule(message: Message):
    await message.answer(
        "📅 <b>Jadval</b>\n\n"
        "Musobaqa jadvali:\n\n"
        "🗓 <b>1-kun:</b> Nazariy test\n"
        "🗓 <b>2-kun:</b> Amaliy topshiriq\n"
        "🗓 <b>3-kun:</b> Final\n\n"
        "<i>Tez orada aniq sanalar qo'shiladi...</i>"
    )

@router.message(F.text == "🏆 My competition")
async def handle_competition(message: Message):
    await message.answer(
        "🏆 <b>Mening Musobaqam</b>\n\n"
        "Sizning ma'lumotlaringiz:\n\n"
        "👤 <b>Ism:</b> Kutilmoqda...\n"
        "🏅 <b>Yo'nalish:</b> Kutilmoqda...\n"
        "📊 <b>Natija:</b> Kutilmoqda...\n\n"
        "<i>Ro'yxatdan o'tganingizdan keyin ko'rinadi</i>"
    )

@router.message(F.text == "🤖 AI assistant")
async def handle_ai(message: Message):
    await message.answer(
        "🤖 <b>AI Assistant</b>\n\n"
        "Salom! Men sizga yordam berishga tayyorman.\n\n"
        "Menga savol bering:\n"
        "- Musobaqa haqida\n"
        "- Topshiriqlar haqida\n"
        "- Texnik yordam\n\n"
        "<i>AI xususiyati tez orada qo'shiladi...</i>"
    )

@router.message(F.text == "⭐ Rating")
async def handle_rating(message: Message):
    await message.answer(
        "⭐ <b>Reyting</b>\n\n"
        "🏆 <b>Top 10 ishtirokchilar:</b>\n\n"
        "1. Ahmadjonov Ali - 950 ball\n"
        "2. Valiyeva Zebo - 920 ball\n"
        "3. Karimov Bobur - 890 ball\n"
        "4. ...\n\n"
        "<i>Tez orada to'liq reyting qo'shiladi...</i>"
    )

@router.message(F.text == "📊 My stats")
async def handle_mystats(message: Message):
    await message.answer(
        "📊 <b>Mening Statistikam</b>\n\n"
        "📝 Topshiriqlar: 0/10\n"
        "✅ To'g'ri javoblar: 0\n"
        "❌ Noto'g'ri javoblar: 0\n"
        "🏆 Ball: 0\n\n"
        "<i>Ro'yxatdan o'tganingizdan keyin ko'rinadi</i>"
    )

# Inline tugmalar uchun handlerlar
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
    await handle_mystats(callback.message)
    await callback.answer()

@router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery):
    await callback.message.answer(
        "🤖 <b>Yordam</b>\n\n"
        "<b>Mavjud buyruqlar:</b>\n"
        "/start - Botni ishga tushirish\n"
        "/app - Mini App\n"
        "/stats - Statistika\n"
        "/help - Yordam"
    )
    await callback.answer()
