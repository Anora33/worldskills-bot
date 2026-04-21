# -*- coding: utf-8 -*-
from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
import sqlite3
import os
import re

logger = logging.getLogger(__name__)
router = Router()

# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "worldskills.db")

# FSM States
class RegisterState(StatesGroup):
    fullname = State()
    phone = State()

# Database helpers
def add_user(tid, fullname, phone, prof_en="", prof_uz=""):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO users VALUES(?,?,?,?,?,?,?)",
                 (str(tid), fullname, phone, prof_en, prof_uz, "pending", None))
        conn.commit()
        conn.close()
        return True
    except: return False

def get_user(tid):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE telegram_id=?", (str(tid),))
        r = c.fetchone()
        conn.close()
        return dict(r) if r else None
    except: return None

# Admin notification
async def notify_admin(bot, text):
    try:
        admin_id = int(os.getenv("ADMIN_ID", 0))
        if admin_id > 0:
            await bot.send_message(admin_id, text, parse_mode="HTML")
            logger.info(f"✅ Admin notified: {admin_id}")
    except Exception as e:
        logger.error(f"notify_admin error: {e}")

# ============= START COMMAND =============
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="👤 Ism-familiyani yuborish", request_contact=True)],
        [KeyboardButton(text="✍️ Qo'lda kiritish")]
    ], resize_keyboard=True, one_time_keyboard=True)
    
    await message.answer(
        "🏆 <b>WorldSkills Shanghai 2026</b>\n\n"
        "👋 <b>Xush kelibsiz!</b>\n\n"
        "📝 <b>1-QADAM: Ism va familiyangizni kiriting</b>\n"
        "<i>Masalan: Ali Valiyev</i>\n\n"
        "Yoki tugmani bosing:",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await state.set_state(RegisterState.fullname)

# ============= FULLNAME HANDLER =============
@router.message(RegisterState.fullname)
async def process_fullname(message: Message, state: FSMContext):
    if message.contact:
        fullname = message.contact.first_name
        if message.contact.last_name:
            fullname += " " + message.contact.last_name
        phone = message.contact.phone_number
        
        await state.update_data(fullname=fullname, phone=phone)
        await message.answer(f"✅ <b>{fullname}</b>\n\n📱 Telefon raqamingiz tasdiqlandi!", 
                           reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")
        await show_categories(message, state, fullname, phone)
        return
    
    if message.text == "✍️ Qo'lda kiritish":
        await message.answer("📝 Ism va familiyangizni kiriting:\n<i>Masalan: Ali Valiyev</i>", parse_mode="HTML")
        return
    
    fullname = message.text.strip()
    
    if not all(c.isalpha() or c.isspace() or c in "'-" for c in fullname):
        await message.answer("❌ <b>Ism-familiya faqat harflardan iborat bo'lishi kerak!</b>\n\nQaytadan kiriting:", parse_mode="HTML")
        return
    
    if len(fullname.split()) < 2:
        await message.answer("❌ <b>Ism va familiyangizni to'liq kiriting!</b>\n\nMasalan: Ali Valiyev\n\nQaytadan kiriting:", parse_mode="HTML")
        return
    
    await state.update_data(fullname=fullname)
    
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📱 Telefon raqamimni yuborish", request_contact=True)],
        [KeyboardButton(text="✍️ Qo'lda kiritish")]
    ], resize_keyboard=True, one_time_keyboard=True)
    
    await message.answer(
        f"✅ <b>{fullname}</b>\n\n"
        f"📱 <b>2-QADAM: Telefon raqamingizni kiriting</b>\n"
        f"<i>Masalan: +998901234567</i>\n\n"
        f"Yoki tugmani bosing:",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await state.set_state(RegisterState.phone)

# ============= PHONE HANDLER =============
@router.message(RegisterState.phone)
async def process_phone(message: Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
        user_data = await state.get_data()
        fullname = user_data.get("fullname")
        await show_categories(message, state, fullname, phone)
        return
    
    if message.text == "✍️ Qo'lda kiritish":
        await message.answer("📱 Telefon raqamingizni kiriting:\n<i>Masalan: +998901234567</i>", parse_mode="HTML")
        return
    
    phone = message.text.strip().replace(" ", "").replace("-", "")
    
    if not re.match(r'^\+?998\d{9}$', phone):
        await message.answer(
            "❌ <b>Telefon raqami noto'g'ri!</b>\n\n"
            "<i>Masalan: +998901234567</i>\n\n"
            "Qaytadan kiriting:",
            parse_mode="HTML"
        )
        return
    
    user_data = await state.get_data()
    fullname = user_data.get("fullname")
    await show_categories(message, state, fullname, phone)

# ============= SHOW CATEGORIES =============
async def show_categories(message: Message, state: FSMContext, fullname, phone):
    categories = [
        ("🏭 Ishlab chiqarish | Manufacturing (17)", "cat1"),
        ("💻 IT va Axborot | IT (8)", "cat2"),
        ("🏗️ Qurilish | Construction (14)", "cat3"),
        ("🚚 Transport | Transport (8)", "cat4"),
        ("🎨 San'at va Moda | Arts (7)", "cat5"),
        ("👥 Xizmatlar | Services (10)", "cat6")
    ]
    
    builder = InlineKeyboardBuilder()
    for name, cat_id in categories:
        builder.button(text=name, callback_data=f"reg_cat_{cat_id}|{fullname}|{phone}")
    builder.adjust(1)
    
    await message.answer(
        "🎓 <b>3-QADAM: Kategoriya tanlang</b>\n\n"
        "6 ta yo'nalishdan birini tanlang:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

# ============= CATEGORY CALLBACK =============
@router.callback_query(F.data.startswith("reg_cat_"))
async def callback_category(callback: types.CallbackQuery, state: FSMContext):
    try:
        data = callback.data.replace("reg_cat_", "")
        parts = data.split("|")
        cat_id = parts[0]
        fullname = parts[1] if len(parts) > 1 else ""
        phone = parts[2] if len(parts) > 2 else ""
        
        professions = {
            "cat1": [
                ("Industrial Mechanics | Sanoat mexanikasi", "p1_1"),
                ("Mechatronics | Mexatronika", "p1_2"),
                ("CNC Turning | CNC tokarlik", "p1_4"),
                ("Welding | Payvandlash", "p1_6"),
                ("Electronics | Elektronika", "p1_7"),
                ("Industry 4.0 | Sanoat 4.0", "p1_10"),
                ("3D Printing | 3D chop etish", "p1_13"),
                ("Renewable Energy | Qayta energiya", "p1_16")
            ],
            "cat2": [
                ("Mobile Apps | Mobil ilovalar", "p2_2"),
                ("Software Development | Dasturiy ta'minot", "p2_3"),
                ("Web Technologies | Veb texnologiyalar", "p2_4"),
                ("Cyber Security | Kiberxavfsizlik", "p2_7")
            ],
            "cat3": [
                ("Wall Tiling | Plitkalash", "p3_1"),
                ("Plumbing | Santexnika", "p3_2"),
                ("Electrical | Elektr", "p3_3"),
                ("Bricklaying | G'isht terish", "p3_4")
            ],
            "cat4": [
                ("Automobile | Avtomobil", "p4_3"),
                ("Logistics | Logistika", "p4_6")
            ],
            "cat5": [
                ("Jewellery | Zargarlik", "p5_1"),
                ("Fashion | Moda", "p5_3"),
                ("Graphic Design | Grafik dizayn", "p5_4")
            ],
            "cat6": [
                ("Cooking | Oshpazlik", "p6_4"),
                ("Hairdressing | Sartaroshlik", "p6_1"),
                ("Health Care | Sog'liqni saqlash", "p6_6")
            ]
        }
        
        profs = professions.get(cat_id, [])
        builder = InlineKeyboardBuilder()
        for name, prof_id in profs:
            builder.button(text=name, callback_data=f"reg_prof_{prof_id}|{fullname}|{phone}|{cat_id}")
        builder.adjust(1)
        
        cat_names = {"cat1":"🏭","cat2":"💻","cat3":"🏗️","cat4":"🚚","cat5":"🎨","cat6":"👥"}
        
        await callback.message.answer(
            f"{cat_names.get(cat_id,'')} <b>Kasblar ro'yxati:</b>\n\n"
            "Kasbingizni tanlang:",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Category error: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)

# ============= PROFESSION CALLBACK =============
@router.callback_query(F.data.startswith("reg_prof_"))
async def callback_profession(callback: types.CallbackQuery, state: FSMContext):
    try:
        data = callback.data.replace("reg_prof_", "")
        parts = data.split("|")
        prof_id = parts[0]
        fullname = parts[1] if len(parts) > 1 else "N/A"
        phone = parts[2] if len(parts) > 2 else "N/A"
        cat_id = parts[3] if len(parts) > 3 else "cat1"
        
        prof_names = {
            "p1_1": "Industrial Mechanics | Sanoat mexanikasi",
            "p1_2": "Mechatronics | Mexatronika",
            "p1_4": "CNC Turning | CNC tokarlik",
            "p1_6": "Welding | Payvandlash",
            "p1_7": "Electronics | Elektronika",
            "p1_10": "Industry 4.0 | Sanoat 4.0",
            "p1_13": "3D Printing | 3D chop etish",
            "p1_16": "Renewable Energy | Qayta energiya",
            "p2_2": "Mobile Apps | Mobil ilovalar",
            "p2_3": "Software Development | Dasturiy ta'minot",
            "p2_4": "Web Technologies | Veb texnologiyalar",
            "p2_7": "Cyber Security | Kiberxavfsizlik",
            "p3_1": "Wall Tiling | Plitkalash",
            "p3_2": "Plumbing | Santexnika",
            "p3_3": "Electrical | Elektr",
            "p3_4": "Bricklaying | G'isht terish",
            "p4_3": "Automobile | Avtomobil",
            "p4_6": "Logistics | Logistika",
            "p5_1": "Jewellery | Zargarlik",
            "p5_3": "Fashion | Moda",
            "p5_4": "Graphic Design | Grafik dizayn",
            "p6_1": "Hairdressing | Sartaroshlik",
            "p6_4": "Cooking | Oshpazlik",
            "p6_6": "Health Care | Sog'liqni saqlash"
        }
        prof_name = prof_names.get(prof_id, prof_id)
        
        add_user(callback.from_user.id, fullname, phone, prof_name, prof_name)
        
        await notify_admin(callback.bot,
            f"🏆 <b>YANGI ISHTIROKCHI RO'YXATDAN O'TDI!</b>\n\n"
            f"👤 <b>Ism:</b> {fullname}\n"
            f"📱 <b>Telefon:</b> {phone}\n"
            f"🔧 <b>Kasb:</b> {prof_name}\n"
            f"🆔 <b>ID:</b> <code>{callback.from_user.id}</code>"
        )
        
        await callback.message.answer(
            f"✅ <b>Tabriklaymiz! Ro'yxatdan o'tdingiz!</b>\n\n"
            f"👤 <b>Ism:</b> {fullname}\n"
            f"📱 <b>Telefon:</b> {phone}\n"
            f"🔧 <b>Kasb:</b> {prof_name}\n\n"
            f"🎉 Endi barcha imkoniyatlardan foydalanishingiz mumkin!",
            parse_mode="HTML"
        )
        
        webapp_url = os.getenv("WEBAPP_URL", "https://worldskills-bot.onrender.com")
        builder = InlineKeyboardBuilder()
        builder.button(text="🤖 AI yordamchi", callback_data="menu_ai")
        builder.button(text="👨‍💼 Admin yordami", callback_data="menu_admin")
        builder.button(text="📄 Mening ma'lumotlarim", callback_data="menu_info")
        builder.button(text="🌐 Mini App ochish", web_app=WebAppInfo(url=webapp_url))
        builder.adjust(2)
        
        await callback.message.answer(
            "📱 <b>Bo'limni tanlang:</b>",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        
        await state.clear()
        await callback.answer()
    except Exception as e:
        logger.error(f"Profession error: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)

# ============= MENU CALLBACKS =============
@router.callback_query(F.data == "menu_ai")
async def callback_ai(callback: types.CallbackQuery):
    await callback.message.answer(
        "🤖 <b>AI Yordamchi</b>\n\n"
        "Savolingizni yozing, men yordam beraman!",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "menu_admin")
async def callback_admin_help(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="📱 Telegram", url="https://t.me/worldskills_admin")
    builder.button(text="📞 Telefon", url="tel:+998933404080")
    builder.button(text="📧 Email", url="mailto:dadaxon45@gmail.com")
    builder.adjust(2)
    
    await callback.message.answer(
        "👨‍💼 <b>Admin Yordami</b>\n\n"
        "📞 <b>Aloqa:</b>\n"
        "• Telegram: @worldskills_admin\n"
        "• Telefon: +998 93 340 40 80\n"
        "• Email: dadaxon45@gmail.com",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "menu_info")
async def callback_info(callback: types.CallbackQuery):
    user = get_user(callback.from_user.id)
    if user:
        await callback.message.answer(
            f"📄 <b>Mening ma'lumotlarim</b>\n\n"
            f"👤 <b>Ism:</b> {user.get('fullname','N/A')}\n"
            f"📱 <b>Telefon:</b> {user.get('phone','N/A')}\n"
            f"🔧 <b>Kasb:</b> {user.get('profession_uz','N/A')}\n"
            f"🆔 <b>ID:</b> <code>{user.get('telegram_id')}</code>",
            parse_mode="HTML"
        )
    else:
        await callback.message.answer("❌ Ma'lumot topilmadi. /start orqali ro'yxatdan o'ting.")
    await callback.answer()
