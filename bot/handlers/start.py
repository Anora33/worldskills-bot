# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

logger = logging.getLogger(__name__)
router = Router()

class UserState(StatesGroup):
    waiting_for_fullname = State()
    waiting_for_phone = State()
    waiting_for_profession = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    logger.info(f"📩 START: user={message.from_user.id}")
    await state.clear()
    
    # Inline keyboard yaratish
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbekcha", callback_data="lang_uz")
    builder.button(text="🇷🇺 Русский", callback_data="lang_ru")
    builder.button(text="🇬🇧 English", callback_data="lang_en")
    builder.adjust(1)
    keyboard = builder.as_markup()
    
    logger.info("📤 Sending welcome message...")
    await message.answer("🌍 <b>Xush kelibsiz!</b>\n\nTilni tanlang:", reply_markup=keyboard)
    logger.info(f"✅ Welcome sent to user={message.from_user.id}")

@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    logger.info(f"🌍 Language selected: {lang}")
    await state.update_data(language=lang)
    await state.set_state(UserState.waiting_for_fullname)
    
    texts = {"uz": "🇺🇿 O'zbek tili tanlandi!\n\n<i>Ism familiyangizni kiriting:</i>", "ru": "🇷🇺 Русский выбран!", "en": "🇬🇧 English selected!"}
    await callback.message.answer(texts.get(lang, texts["uz"]))
    await callback.answer()

@router.message(UserState.waiting_for_fullname)
async def process_fullname(message: Message, state: FSMContext):
    logger.info(f"📝 Fullname received: {message.text}")
    fullname = message.text.strip()
    if len(fullname) < 3:
        await message.answer("❌ Ism juda qisqa!")
        return
    await state.update_data(fullname=fullname)
    await state.set_state(UserState.waiting_for_phone)
    await message.answer(f"✅ {fullname}\n\n<b>Telefon raqamingizni kiriting:</b>")

@router.message(UserState.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    logger.info(f"📝 Phone received: {message.text}")
    phone = message.text.strip()
    if not phone.startswith("+") or len(phone) < 12:
        await message.answer("❌ Telefon noto'g'ri! Masalan: +998901234567")
        return
    await state.update_data(phone=phone)
    await state.set_state(UserState.waiting_for_profession)
    
    # Kasb tanlash keyboard
    builder = InlineKeyboardBuilder()
    professions = ["💻 Dasturlash", "🎨 Dizayn", "🔧 Mexanika", "🏗 Qurilish", "👨‍🍳 Oshpazlik", "💼 Biznes"]
    for prof in professions:
        builder.button(text=prof, callback_data=f"prof_{prof.split()[-1].lower()}")
    builder.adjust(2)
    
    await message.answer("✅ Telefon qabul qilindi\n\n<b>Kasbingizni tanlang:</b>", reply_markup=builder.as_markup())

@router.callback_query(UserState.waiting_for_profession)
async def process_profession(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", "uz")
    logger.info(f"🎉 Registration complete for user={callback.from_user.id}")
    await state.clear()
    
    # Asosiy menyu
    builder = ReplyKeyboardBuilder()
    menu = ["📱 Mini App", "📊 Mening statistikam", "🏆 Mening musobaqam", "🤖 AI yordamchi", "⭐ Reyting", "👨‍💼 Admin yordami"]
    for btn in menu:
        builder.button(text=btn)
    builder.adjust(1, 2, 2, 1)
    
    await callback.message.answer("🎉 <b>Ro'yxatdan o'tdingiz!</b>", reply_markup=builder.as_markup())
    await callback.answer()

# Menu tugmalari
@router.message(F.text == "📱 Mini App")
async def handle_mini_app(message: Message):
    logger.info("📱 Mini App clicked")
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Ochish", web_app=WebAppInfo(url="https://worldskills-webapp.vercel.app"))
    await message.answer("📱 <b>Mini App</b>", reply_markup=builder.as_markup())

@router.message(F.text == "🤖 AI yordamchi")
async def handle_ai(message: Message, state: FSMContext):
    logger.info("🤖 AI clicked")
    await state.update_data(ai_active=True)
    await message.answer("🤖 <b>AI Yordamchi</b>\n\nSavolingizni yozing:")

@router.message(F.text == "📊 Mening statistikam")
async def handle_stats(message: Message):
    logger.info("📊 Stats clicked")
    await message.answer("📊 Statistika tez orada...")

@router.message(F.text == "🏆 Mening musobaqam")
async def handle_competition(message: Message):
    logger.info("🏆 Competition clicked")
    await message.answer("🏆 Musobaqa ma'lumotlari tez orada...")

@router.message(F.text == "⭐ Reyting")
async def handle_rating(message: Message):
    logger.info("⭐ Rating clicked")
    await message.answer("⭐ Reyting tez orada...")

@router.message(F.text == "👨‍💼 Admin yordami")
async def handle_admin(message: Message):
    logger.info("👨‍💼 Admin clicked")
    await message.answer("👨‍💼 Admin: @admin_username")
