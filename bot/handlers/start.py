# -*- coding: utf-8 -*-
from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, WebAppInfo, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

# Til tanlash uchun inline tugmalar
def get_language_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbekcha", callback_data="lang_uz")
    builder.button(text="🇷🇺 Русский", callback_data="lang_ru")
    builder.button(text="🇬🇧 English", callback_data="lang_en")
    builder.adjust(1)
    return builder.as_markup()

# Asosiy menyu (ReplyKeyboard)
def get_main_menu(lang="uz"):
    texts = {
        "uz": {
            "mini_app": "📱 Mini App",
            "registration": "📝 Ro'yxatdan o'tish",
            "my_stats": "📊 Mening statistikam",
            "schedule": "📅 Jadval",
            "my_competition": "🏆 Mening musobaqam",
            "ai_assistant": "🤖 AI yordamchi",
            "rating": "⭐ Reyting",
            "admin_help": "👨‍ Admin yordami"
        },
        "ru": {
            "mini_app": "📱 Mini App",
            "registration": "📝 Регистрация",
            "my_stats": "📊 Моя статистика",
            "schedule": "📅 Расписание",
            "my_competition": "🏆 Моё соревнование",
            "ai_assistant": "🤖 AI помощник",
            "rating": "⭐ Рейтинг",
            "admin_help": "👨‍💼 Помощь админа"
        },
        "en": {
            "mini_app": "📱 Mini App",
            "registration": "📝 Registration",
            "my_stats": "📊 My statistics",
            "schedule": "📅 Schedule",
            "my_competition": "🏆 My competition",
            "ai_assistant": "🤖 AI assistant",
            "rating": "⭐ Rating",
            "admin_help": "👨‍💼 Admin help"
        }
    }
    
    t = texts.get(lang, texts["uz"])
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=t["mini_app"]))
    builder.row(KeyboardButton(text=t["registration"]))
    builder.row(KeyboardButton(text=t["my_stats"]))
    builder.row(KeyboardButton(text=t["schedule"]))
    builder.row(
        KeyboardButton(text=t["my_competition"]),
        KeyboardButton(text=t["ai_assistant"])
    )
    builder.row(
        KeyboardButton(text=t["rating"]),
        KeyboardButton(text=t["admin_help"])
    )
    return builder.as_markup(resize_keyboard=True)

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Til tanlash"""
    await message.answer(
        "🌍 <b>Tilni tanlang / Choose language / Выберите язык</b>\n\n"
        "Botdan foydalanish uchun tilni tanlang:",
        reply_markup=get_language_keyboard()
    )

# Til tanlash handleri
@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    
    texts = {
        "uz": "🇺 O'zbek tili tanlandi!\n\nBotdan foydalanishga xush kelibsiz!",
        "ru": "🇷🇺 Русский язык выбран!\n\nДобро пожаловать в бот!",
        "en": "🇬🇧 English selected!\n\nWelcome to the bot!"
    }
    
    await callback.message.answer(
        texts.get(lang, texts["uz"]),
        reply_markup=get_main_menu(lang)
    )
    await callback.answer()

# Menu tugmalari handlerlari
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

@router.message(F.text == "📝 Ro'yxatdan o'tish" or F.text == "📝 Регистрация" or F.text == "📝 Registration")
async def handle_registration(message: Message):
    await message.answer(
        "📝 <b>Ro'yxatdan O'tish</b>\n\n"
        "Quyidagi ma'lumotlarni kiriting:\n\n"
        "1️⃣ <b>Ism Familiya:</b>\n"
        "2️⃣ <b>Telefon raqam:</b>\n"
        "3️⃣ <b>WorldSkills yo'nalishi:</b>\n\n"
        "<i>Tez orada to'liq forma qo'shiladi...</i>"
    )

@router.message(F.text == "📊 Mening statistikam" or F.text == "📊 Моя статистика" or F.text == "📊 My statistics")
async def handle_stats(message: Message):
    await message.answer(
        "📊 <b>Mening Statistikam</b>\n\n"
        "📝 Topshiriqlar: 0/10\n"
        "✅ To'g'ri javoblar: 0\n"
        "❌ Noto'g'ri javoblar: 0\n"
        "🏆 Ball: 0\n\n"
        "<i>Ro'yxatdan o'tganingizdan keyin ko'rinadi</i>"
    )

@router.message(F.text == "📅 Jadval" or F.text == "📅 Расписание" or F.text == "📅 Schedule")
async def handle_schedule(message: Message):
    await message.answer(
        "📅 <b>Jadval</b>\n\n"
        "Musobaqa jadvali:\n\n"
        "🗓 <b>1-kun:</b> Nazariy test\n"
        "🗓 <b>2-kun:</b> Amaliy topshiriq\n"
        "🗓 <b>3-kun:</b> Final\n\n"
        "<i>Tez orada aniq sanalar qo'shiladi...</i>"
    )

@router.message(F.text == "🏆 Mening musobaqam" or F.text == "🏆 Моё соревнование" or F.text == "🏆 My competition")
async def handle_competition(message: Message):
    await message.answer(
        "🏆 <b>Mening Musobaqam</b>\n\n"
        "Sizning ma'lumotlaringiz:\n\n"
        "👤 <b>Ism:</b> Kutilmoqda...\n"
        "🏅 <b>Yo'nalish:</b> Kutilmoqda...\n"
        "📊 <b>Natija:</b> Kutilmoqda...\n\n"
        "<i>Ro'yxatdan o'tganingizdan keyin ko'rinadi</i>"
    )

@router.message(F.text == "🤖 AI yordamchi" or F.text == "🤖 AI помощник" or F.text == "🤖 AI assistant")
async def handle_ai(message: Message):
    await message.answer(
        "🤖 <b>AI Yordamchi</b>\n\n"
        "Salom! Men sizga yordam berishga tayyorman.\n\n"
        "Menga savol bering:\n"
        "- Musobaqa haqida\n"
        "- Topshiriqlar haqida\n"
        "- Texnik yordam\n\n"
        "<i>Savolingizni yozing, men javob beraman!</i>"
    )

@router.message(F.text == "⭐ Reyting" or F.text == "⭐ Рейтинг" or F.text == "⭐ Rating")
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

@router.message(F.text == "👨‍💼 Admin yordami" or F.text == "👨‍ Помощь админа" or F.text == "👨‍💼 Admin help")
async def handle_admin(message: Message):
    await message.answer(
        "👨‍💼 <b>Admin Yordami</b>\n\n"
        "Savollaringiz bo'lsa, admin bilan bog'laning:\n\n"
        "📱 Telegram: @admin_username\n"
        "📧 Email: admin@worldskills.uz\n"
        "📞 Telefon: +998 90 123 45 67\n\n"
        "<i>Tez orada javob beramiz!</i>"
    )
