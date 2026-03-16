# -*- coding: utf-8 -*-
# ✅ AIOTELEGRAM 3.x IMPORTS
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, WebAppInfo, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext  # ✅ 3.x: fsm.context
from aiogram.fsm.state import State, StatesGroup  # ✅ 3.x: fsm.state
from bot.config import WEBAPP_URL, ADMIN_ID
from bot.database.db import get_user, add_user
import logging, asyncio

logger = logging.getLogger(__name__)
router = Router()

class UserState(StatesGroup):
    waiting_for_fullname = State()
    waiting_for_phone = State()
    waiting_for_profession = State()

async def notify_admin(bot, tid, fullname, profession):
    try:
        await bot.send_message(ADMIN_ID, f"🔔 Yangi ishtirokchi!\n\n👤 ID: {tid}\n👤 Ism: {fullname}\n🎓 Kompetensiya: {profession}")
    except: pass

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    tid = message.from_user.id
    user = get_user(tid)
    
    if user:
        kb = ReplyKeyboardBuilder()
        buttons = ["📱 Mini App", "📊 Mening statistikam", "🏆 Mening musobaqam", "🤖 AI yordamchi", "⭐ Reyting", "👨‍💼 Admin yordami"]
        for btn in buttons:
            kb.row(KeyboardButton(text=btn))
        
        await message.answer(
            f"👋 <b>Xush kelibsiz, {user.get('fullname', 'Foydalanuvchi')}!</b>\n\n"
            f"📊 <b>Profilingiz:</b>\n"
            f"• Kasb: {user.get('profession')}\n"
            f"• Telefon: {user.get('phone')}\n"
            f"• Baho: {user.get('admin_score', 0)}/100\n\n"
            f"Kerakli bo'limni tanlang:",
            reply_markup=kb.as_markup(resize_keyboard=True),
            parse_mode="HTML"
        )
        return
    
    await state.clear()
    kb = InlineKeyboardBuilder()
    kb.button(text="🇺🇿 O'zbekcha", callback_data="lang_uz")
    kb.button(text="🇷🇺 Русский", callback_data="lang_ru")
    kb.button(text="🇬🇧 English", callback_data="lang_en")
    kb.adjust(1)
    await message.answer("🌍 <b>Tilni tanlang:</b>", reply_markup=kb.as_markup(), parse_mode="HTML")

@router.callback_query(F.data.startswith("lang_"))
async def set_lang(cb: CallbackQuery, state: FSMContext):
    lang = cb.data.split("_")[1]
    await state.update_data(language=lang)
    await state.set_state(UserState.waiting_for_fullname)
    await cb.message.answer("📝 <b>Ism familiyangizni kiriting:</b>")
    await cb.answer()

@router.message(UserState.waiting_for_fullname)
async def proc_name(msg: Message, state: FSMContext):
    fn = msg.text.strip()
    if len(fn) < 3:
        await msg.answer("❌ Ism juda qisqa!")
        return
    await state.update_data(fullname=fn)
    await state.set_state(UserState.waiting_for_phone)
    await msg.answer("📱 <b>Telefon raqamingizni kiriting:</b>\n<i>+998901234567</i>", parse_mode="HTML")

@router.message(UserState.waiting_for_phone)
async def proc_phone(msg: Message, state: FSMContext):
    ph = msg.text.strip()
    if not ph.startswith("+") or len(ph) < 12:
        await msg.answer("❌ Telefon noto'g'ri!")
        return
    await state.update_data(phone=ph)
    await state.set_state(UserState.waiting_for_profession)
    
    kb = InlineKeyboardBuilder()
    kb.button(text="💻 Dasturlash", callback_data="prof_Dasturlash")
    kb.button(text="🎨 Dizayn", callback_data="prof_Dizayn")
    kb.button(text="🔧 Mexanika", callback_data="prof_Mexanika")
    kb.button(text="🏗 Qurilish", callback_data="prof_Qurilish")
    kb.button(text="👨‍🍳 Oshpazlik", callback_data="prof_Oshpazlik")
    kb.button(text="💼 Biznes", callback_data="prof_Biznes")
    kb.adjust(2)
    await msg.answer("🎓 <b>Kasbingizni tanlang:</b>", reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("prof_"))
async def proc_prof(cb: CallbackQuery, state: FSMContext):
    d = await state.get_data()
    fullname = d.get("fullname", "")
    profession = cb.data.replace("prof_", "")
    tid = cb.from_user.id
    phone = d.get("phone", "")
    lang = d.get("language", "uz")
    
    add_user(tid, fullname, phone, profession, lang)
    asyncio.create_task(notify_admin(cb.bot, tid, fullname, profession))
    
    kb = ReplyKeyboardBuilder()
    buttons = ["📱 Mini App", "📊 Mening statistikam", "🏆 Mening musobaqam", "🤖 AI yordamchi", "⭐ Reyting", "👨‍💼 Admin yordami"]
    for btn in buttons:
        kb.row(KeyboardButton(text=btn))
    
    await cb.message.answer(
        "🎉 <b>Muvaffaqiyatli ro'yxatdan o'tdingiz!</b>\n\n"
        "✅ <b>Ma'lumotlaringiz saqlandi.</b>\n"
        "🔔 <b>Admin xabardor qilindi.</b>\n\n"
        "🎯 <b>Kerakli bo'limni tanlang:</b>",
        reply_markup=kb.as_markup(resize_keyboard=True),
        parse_mode="HTML"
    )
    await cb.answer()

@router.message(F.text == "📱 Mini App")
async def mini_app(msg: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Ochish", web_app=WebAppInfo(url=WEBAPP_URL))
    await msg.answer("📱 <b>Mini App</b>", reply_markup=kb.as_markup(), parse_mode="HTML")

@router.message(F.text == "📊 Mening statistikam")
async def stats(msg: Message):
    user = get_user(msg.from_user.id)
    if user:
        await msg.answer(f"📊 <b>Statistika</b>\n\n👤 Ism: {user.get('fullname')}\n🎓 Kasb: {user.get('profession')}\n⭐ Ball: {user.get('admin_score', 0)}/100", parse_mode="HTML")

@router.message(F.text == "🏆 Mening musobaqam")
async def comp(msg: Message):
    await msg.answer("🏆 <b>Musobaqa</b>\n\nTez orada...", parse_mode="HTML")

@router.message(F.text == "⭐ Reyting")
async def rating(msg: Message):
    await msg.answer("⭐ <b>Reyting</b>\n\nTez orada...", parse_mode="HTML")

@router.message(F.text == "👨‍💼 Admin yordami")
async def admin_help(msg: Message):
    await msg.answer("👨‍💼 <b>Admin yordami</b>\n\n📞 Telegram: @worldskills_admin", parse_mode="HTML")
