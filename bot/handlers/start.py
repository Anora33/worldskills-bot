# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, WebAppInfo, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.config import WEBAPP_URL, ADMIN_ID
from bot.database.db import get_user, add_user
import logging, asyncio

logger = logging.getLogger(__name__)
router = Router()

class UserState(StatesGroup):
    waiting_for_fullname = State()
    waiting_for_phone = State()
    waiting_for_profession = State()

async def notify_admin(bot, tid, fullname, profession, phone):
    """Admin'ga to'liq ma'lumot yuborish"""
    try:
        await bot.send_message(
            ADMIN_ID,
            f"🔔 <b>YANGI ISHTIROKCHI!</b>\n\n"
            f"👤 <b>To'liq ism:</b> {fullname}\n"
            f"📱 <b>Telefon:</b> {phone}\n"
            f"🎓 <b>Kompetensiya:</b> {profession}\n"
            f"🆔 <b>ID:</b> <code>{tid}</code>\n\n"
            f"⏳ <b>Status:</b> Kutilmoqda\n\n"
            f"<i>Admin panel: /admin</i>",
            parse_mode="HTML"
        )
        logger.info(f"✅ Admin notified: {tid}")
    except Exception as e:
        logger.error(f"❌ Admin notification error: {e}")

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    tid = message.from_user.id
    user = get_user(tid)
    
    if user:
        # Professional menu buttons
        kb = ReplyKeyboardBuilder()
        buttons = [
            "📱 WorldSkills App",
            "📊 Mening Natijalarim", 
            "🏆 Musobaqalar",
            "🤖 AI Yordamchi",
            "📊 Reyting",
            "👨‍💼 Admin Yordami"
        ]
        for btn in buttons:
            kb.row(KeyboardButton(text=btn))
        
        await message.answer(
            f"🏆 <b>WorldSkills Uzbekistan</b>\n\n"
            f"👋 <b>Xush kelibsiz, {user.get('fullname')}!</b>\n\n"
            f"📊 <b>Sizning Profilingiz:</b>\n"
            f"• Kompetensiya: {user.get('profession')}\n"
            f"• Telefon: {user.get('phone')}\n"
            f"• Ball: {user.get('admin_score', 0)}/100\n\n"
            f"Kerakli bo'limni tanlang:",
            reply_markup=kb.as_markup(resize_keyboard=True),
            parse_mode="HTML"
        )
        return
    
    # New user registration
    await state.clear()
    kb = InlineKeyboardBuilder()
    kb.button(text="🇺🇿 O'zbekcha", callback_data="lang_uz")
    kb.button(text="🇷🇺 Русский", callback_data="lang_ru")
    kb.button(text="🇬🇧 English", callback_data="lang_en")
    kb.adjust(1)
    
    await message.answer(
        "🏆 <b>WorldSkills Uzbekistan</b>\n\n"
        "<i>Kasbiy mahorat musobaqasida ishtirok etish uchun ro'yxatdan o'ting</i>",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("lang_"))
async def set_lang(cb: CallbackQuery, state: FSMContext):
    lang = cb.data.split("_")[1]
    await state.update_data(language=lang)
    await state.set_state(UserState.waiting_for_fullname)
    await cb.message.answer(
        "📝 <b>Ro'yxatdan o'tish</b>\n\n"
        "<b>Ism va familiyangizni kiriting:</b>",
        parse_mode="HTML"
    )
    await cb.answer()

@router.message(UserState.waiting_for_fullname)
async def proc_name(msg: Message, state: FSMContext):
    fn = msg.text.strip()
    if len(fn) < 3:
        await msg.answer("❌ <b>Ism juda qisqa!</b>\n\nIsm va familiyangizni to'liq kiriting.", parse_mode="HTML")
        return
    await state.update_data(fullname=fn)
    await state.set_state(UserState.waiting_for_phone)
    await msg.answer(
        f"✅ <b>{fn}</b>\n\n"
        f"📱 <b>Telefon raqamingizni kiriting:</b>\n"
        f"<i>Masalan: +998 90 123 45 67</i>",
        parse_mode="HTML"
    )

@router.message(UserState.waiting_for_phone)
async def proc_phone(msg: Message, state: FSMContext):
    ph = msg.text.strip()
    if not ph.startswith("+") or len(ph.replace(" ", "")) < 12:
        await msg.answer("❌ <b>Telefon noto'g'ri!</b>\n\nMasalan: +998 90 123 45 67", parse_mode="HTML")
        return
    await state.update_data(phone=ph)
    await state.set_state(UserState.waiting_for_profession)
    
    kb = InlineKeyboardBuilder()
    professions = [
        "💻 Dasturlash",
        "💻 Web texnologiyalar",
        "🎨 Dizayn",
        "🔧 Mexanika",
        "🏗 Qurilish",
        "👨‍🍳 Oshpazlik",
        "💼 Biznes"
    ]
    for prof in professions:
        kb.button(text=prof, callback_data=f"prof_{prof.replace(' ', '_')}")
    kb.adjust(2)
    
    await msg.answer(
        "✅ <b>Telefon qabul qilindi</b>\n\n"
        "🎓 <b>Kompetensiyangizni tanlang:</b>",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("prof_"))
async def proc_prof(cb: CallbackQuery, state: FSMContext):
    d = await state.get_data()
    fullname = d.get("fullname", "")
    profession = cb.data.replace("prof_", "").replace("_", " ")
    tid = cb.from_user.id
    phone = d.get("phone", "")
    lang = d.get("language", "uz")
    
    # Save to database
    add_user(tid, fullname, phone, profession, lang)
    
    # Notify admin with full info
    asyncio.create_task(notify_admin(cb.bot, tid, fullname, profession, phone))
    
    # Professional menu
    kb = ReplyKeyboardBuilder()
    buttons = [
        "📱 WorldSkills App",
        "📊 Mening Natijalarim",
        "🏆 Musobaqalar",
        "🤖 AI Yordamchi",
        "📊 Reyting",
        "👨‍💼 Admin Yordami"
    ]
    for btn in buttons:
        kb.row(KeyboardButton(text=btn))
    
    await cb.message.answer(
        "🎉 <b>Muvaffaqiyatli Ro'yxatdan O'tdingiz!</b>\n\n"
        "✅ <b>Ma'lumotlaringiz qabul qilindi</b>\n"
        "🔔 <b>Admin xabardor qilindi</b>\n"
        "⏳ <b>Admin tasdiqini kuting</b>\n\n"
        "📌 <i>Tasdiqlangandan so'ng SMS xabar yuboriladi</i>\n\n"
        "🎯 <b>Kerakli bo'limni tanlang:</b>",
        reply_markup=kb.as_markup(resize_keyboard=True),
        parse_mode="HTML"
    )
    await cb.answer()

@router.message(F.text == "📱 WorldSkills App")
async def mini_app(msg: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 WorldSkills App'ni Ochish", web_app=WebAppInfo(url=WEBAPP_URL))
    await msg.answer(
        "📱 <b>WorldSkills Mobile App</b>\n\n"
        "📸 <b>Portfolio yuklash:</b> Ishlaringizni yuklang\n"
        "📊 <b>Natijalar:</b> Yutuqlaringizni ko'ring\n"
        "🏆 <b>Sertifikatlar:</b> Yutuq sertifikatlari\n\n"
        "<i>Barcha imkoniyatlardan foydalanish uchun App'ni oching:</i>",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )

@router.message(F.text == "📊 Mening Natijalarim")
async def stats(msg: Message):
    user = get_user(msg.from_user.id)
    if user:
        status_emoji = {"pending":"⏳","approved":"✅","rejected":"❌"}.get(user.get("status"),"⏳")
        await msg.answer(
            f"📊 <b>Sizning Natijalaringiz</b>\n\n"
            f"👤 <b>To'liq ism:</b> {user.get('fullname')}\n"
            f"🎓 <b>Kompetensiya:</b> {user.get('profession')}\n"
            f"📅 <b>Ro'yxatdan o'tgan:</b> {user.get('registered_at', 'Noma\\lum')}\n"
            f"📊 <b>Status:</b> {status_emoji} {user.get('status', 'pending').title()}\n"
            f"⭐ <b>Ball:</b> {user.get('admin_score', 0)}/100\n\n"
            f"<i>Admin tomonidan tekshirilgandan so'ng ballaringiz ko'rinadi</i>",
            parse_mode="HTML"
        )

@router.message(F.text == "🏆 Musobaqalar")
async def comp(msg: Message):
    await msg.answer(
        "🏆 <b>WorldSkills Musobaqalari</b>\n\n"
        "📅 <b>Keyingi bosqichlar:</b>\n"
        "• Mintaqaviy bosqich: Tez orada\n"
        "• Milliy bosqich: Tez orada\n"
        "• Xalqaro bosqich: Tez orada\n\n"
        "📌 <i>Ro'yxatdan o'tgan ishtirokchilarga SMS orqali xabar yuboriladi</i>\n\n"
        "🎯 <b>Tayyorgarlik ko'ring!</b>",
        parse_mode="HTML"
    )

@router.message(F.text == "🤖 AI Yordamchi")
async def ai_start(msg: Message, state: FSMContext):
    await state.update_data(ai_active=True)
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="🔙 Bosh Menyu"))
    await msg.answer(
        "🤖 <b>WorldSkills AI Yordamchisi</b>\n\n"
        "🎯 <b>Men sizga quyidagilarda yordam bera olaman:</b>\n\n"
        "• WorldSkills haqida ma'lumot\n"
        "• Kompetensiyalar bo'yicha maslahat\n"
        "• Tayyorgarlik rejasi\n"
        "• Baholash mezonlari\n"
        "• Umumiy savollar\n\n"
        "<b>Savolingizni yozing:</b>",
        reply_markup=kb.as_markup(resize_keyboard=True),
        parse_mode="HTML"
    )

@router.message(F.text == "🔙 Bosh Menyu")
async def ai_exit(msg: Message, state: FSMContext):
    await state.update_data(ai_active=False)
    await state.clear()
    kb = ReplyKeyboardBuilder()
    buttons = ["📱 WorldSkills App", "📊 Mening Natijalarim", "🏆 Musobaqalar", "🤖 AI Yordamchi", "📊 Reyting", "👨‍💼 Admin Yordami"]
    for btn in buttons:
        kb.row(KeyboardButton(text=btn))
    await msg.answer(
        "✅ <b>Bosh menyuga qaytdingiz</b>\n\n"
        "Kerakli bo'limni tanlang:",
        reply_markup=kb.as_markup(resize_keyboard=True),
        parse_mode="HTML"
    )

@router.message(F.text == "📊 Reyting")
async def rating(msg: Message):
    await msg.answer(
        "📊 <b>Ishtirokchilar Reytingi</b>\n\n"
        "🥇 1. Ishtirokchi - 95 ball\n"
        "🥈 2. Ishtirokchi - 92 ball\n"
        "🥉 3. Ishtirokchi - 89 ball\n\n"
        "<i>Reyting admin tomonidan yangilanadi</i>",
        parse_mode="HTML"
    )

@router.message(F.text == "👨‍💼 Admin Yordami")
async def admin_help(msg: Message):
    await msg.answer(
        "👨‍💼 <b>Admin Yordami</b>\n\n"
        "📞 <b>Aloqa:</b>\n"
        "• Telegram: @worldskills_admin\n"
        "• Telefon: +998 71 123 45 67\n"
        "• Email: info@worldskills.uz\n\n"
        "🕐 <b>Ish vaqti:</b>\n"
        "Dushanba - Juma: 9:00 - 18:00\n\n"
        "<i>Savollaringiz bo'lsa, murojaat qiling!</i>",
        parse_mode="HTML"
    )
