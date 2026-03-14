# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

logger = logging.getLogger(__name__)
router = Router()

# States
class UserState(StatesGroup):
    waiting_for_fullname = State()
    waiting_for_phone = State()
    waiting_for_profession = State()

# Keyboards
def get_language_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbekcha", callback_data="lang_uz")
    builder.button(text="🇷🇺 Русский", callback_data="lang_ru")
    builder.button(text="🇬🇧 English", callback_data="lang_en")
    builder.adjust(1)
    return builder.as_markup()

def get_profession_keyboard(lang):
    texts = {
        "uz": ["💻 Dasturlash", "🎨 Dizayn", "🔧 Mexanika", "🏗 Qurilish", "👨‍🍳 Oshpazlik", "💼 Biznes"],
        "ru": ["💻 Программирование", "🎨 Дизайн", "🔧 Механика", "🏗 Строительство", "👨‍🍳 Кулинария", "💼 Бизнес"],
        "en": ["💻 Programming", "🎨 Design", "🔧 Mechanics", "🏗 Construction", "👨‍🍳 Cooking", "💼 Business"]
    }
    builder = InlineKeyboardBuilder()
    for btn in texts.get(lang, texts["uz"]):
        builder.button(text=btn, callback_data=f"prof_{btn.split()[-1].lower()}")
    builder.adjust(2)
    return builder.as_markup()

def get_main_menu_keyboard(lang):
    texts = {
        "uz": {"mini_app": "📱 Mini App", "my_stats": "📊 Mening statistikam", "my_competition": "🏆 Mening musobaqam", "ai_assistant": "🤖 AI yordamchi", "rating": "⭐ Reyting", "admin_help": "👨‍💼 Admin yordami", "change_profession": "🔄 Kasbni o'zgartirish"},
        "ru": {"mini_app": "📱 Mini App", "my_stats": "📊 Моя статистика", "my_competition": "🏆 Моё соревнование", "ai_assistant": "🤖 AI помощник", "rating": "⭐ Рейтинг", "admin_help": "👨‍💼 Помощь админа", "change_profession": "🔄 Сменить профессию"},
        "en": {"mini_app": "📱 Mini App", "my_stats": "📊 My statistics", "my_competition": "🏆 My competition", "ai_assistant": "🤖 AI assistant", "rating": "⭐ Rating", "admin_help": "👨‍💼 Admin help", "change_profession": "🔄 Change profession"}
    }
    t = texts.get(lang, texts["uz"])
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=t["mini_app"]))
    builder.row(KeyboardButton(text=t["my_stats"]))
    builder.row(KeyboardButton(text=t["my_competition"]), KeyboardButton(text=t["ai_assistant"]))
    builder.row(KeyboardButton(text=t["rating"]), KeyboardButton(text=t["admin_help"]))
    builder.row(KeyboardButton(text=t["change_profession"]))
    return builder.as_markup(resize_keyboard=True)

# ========== HANDLERS ==========

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    logger.info(f"📩 /start from user {message.from_user.id}")
    await state.clear()
    await message.answer(
        "🌍 <b>Xush kelibsiz!</b>\n\nTilni tanlang:",
        reply_markup=get_language_keyboard()
    )
    logger.info(f"✅ Welcome sent to {message.from_user.id}")

@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(language=lang)
    await state.set_state(UserState.waiting_for_fullname)
    
    texts = {"uz": "🇺🇿 O'zbek tili tanlandi!\n\n<i>Ism familiyangizni kiriting:</i>", "ru": "🇷🇺 Русский выбран!\n\n<i>Введите имя:</i>", "en": "🇬🇧 English selected!\n\n<i>Enter your name:</i>"}
    await callback.message.answer(texts.get(lang, texts["uz"]))
    await callback.answer()

@router.message(UserState.waiting_for_fullname)
async def process_fullname(message: Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", "uz")
    fullname = message.text.strip()
    if len(fullname) < 3:
        await message.answer({"uz": "❌ Ism juda qisqa!", "ru": "❌ Имя короткое!", "en": "❌ Name too short!"}.get(lang, "❌"))
        return
    await state.update_data(fullname=fullname)
    await state.set_state(UserState.waiting_for_phone)
    await message.answer({"uz": f"✅ {fullname}\n\n<b>Telefon:</b>", "ru": f"✅ {fullname}\n\n<b>Телефон:</b>", "en": f"✅ {fullname}\n\n<b>Phone:</b>"}.get(lang, ""))

@router.message(UserState.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", "uz")
    phone = message.text.strip()
    if not phone.startswith("+") or len(phone) < 12:
        await message.answer({"uz": "❌ Telefon noto'g'ri!", "ru": "❌ Неверный телефон!", "en": "❌ Invalid phone!"}.get(lang, "❌"))
        return
    await state.update_data(phone=phone)
    await state.set_state(UserState.waiting_for_profession)
    await message.answer({"uz": "✅ Telefon\n\n<b>Kasb tanlang:</b>", "ru": "✅ Телефон\n\n<b>Профессия:</b>", "en": "✅ Phone\n\n<b>Profession:</b>"}.get(lang, ""), reply_markup=get_profession_keyboard(lang))

@router.callback_query(UserState.waiting_for_profession)
async def process_profession(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", "uz")
    await state.clear()
    texts = {"uz": "🎉 Ro'yxatdan o'tdingiz!", "ru": "🎉 Регистрация завершена!", "en": "🎉 Registration complete!"}
    await callback.message.answer(texts.get(lang, texts["uz"]), reply_markup=get_main_menu_keyboard(lang))
    await callback.answer()

# Menu buttons
@router.message(F.text == "📱 Mini App")
async def handle_mini_app(message: Message):
    await message.answer("📱 <b>Mini App</b>", reply_markup=InlineKeyboardBuilder().button(text="🚀 Ochish", web_app=WebAppInfo(url="https://worldskills-webapp.vercel.app")).as_markup())

@router.message(F.text == "🤖 AI yordamchi" or F.text == "🤖 AI помощник" or F.text == "🤖 AI assistant")
async def handle_ai(message: Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", "uz")
    await state.update_data(ai_active=True)
    texts = {"uz": "🤖 <b>AI Yordamchi</b>\n\nSavolingizni yozing:", "ru": "🤖 <b>AI Помощник</b>\n\nНапишите вопрос:", "en": "🤖 <b>AI Assistant</b>\n\nType your question:"}
    await message.answer(texts.get(lang, texts["uz"]))

@router.message(F.text == "📊 Mening statistikam" or F.text == "📊 Моя статистика" or F.text == "📊 My statistics")
async def handle_stats(message: Message):
    await message.answer("📊 Statistika tez orada...")

@router.message(F.text == "🏆 Mening musobaqam" or F.text == "🏆 Моё соревнование" or F.text == "🏆 My competition")
async def handle_competition(message: Message):
    await message.answer("🏆 Musobaqa tez orada...")

@router.message(F.text == "⭐ Reyting" or F.text == "⭐ Рейтинг" or F.text == "⭐ Rating")
async def handle_rating(message: Message):
    await message.answer("⭐ Reyting tez orada...")

@router.message(F.text == "👨‍💼 Admin yordami" or F.text == "👨‍💼 Помощь админа" or F.text == "👨‍💼 Admin help")
async def handle_admin(message: Message):
    await message.answer("👨‍💼 Admin: @admin_username")

@router.message(F.text == "🔄 Kasbni o'zgartirish" or F.text == "🔄 Сменить профессию" or F.text == "🔄 Change profession")
async def handle_change_profession(message: Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", "uz")
    await state.set_state(UserState.waiting_for_profession)
    await message.answer({"uz": "<b>Kasb tanlang:</b>", "ru": "<b>Профессия:</b>", "en": "<b>Profession:</b>"}.get(lang, ""), reply_markup=get_profession_keyboard(lang))

@router.message(Command("start"))
async def exit_any_state(message: Message, state: FSMContext):
    await state.clear()
    await cmd_start(message, state)
