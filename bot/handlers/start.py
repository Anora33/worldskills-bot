# -*- coding: utf-8 -*-
from aiogram import Router, F, types
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
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            telegram_id TEXT PRIMARY KEY,
            fullname TEXT,
            phone TEXT,
            profession_en TEXT,
            profession_uz TEXT,
            status TEXT DEFAULT 'pending',
            registered_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT,
            doc_id TEXT,
            doc_title TEXT,
            filename TEXT,
            status TEXT DEFAULT 'pending',
            score INTEGER DEFAULT 0,
            comment TEXT,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT,
            profession_id TEXT,
            filename TEXT,
            file_type TEXT,
            status TEXT DEFAULT 'pending',
            score INTEGER DEFAULT 0,
            comment TEXT,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ DB init error: {e}")

def add_user(tid, fullname, phone, prof_en="", prof_uz=""):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO users VALUES(?,?,?,?,?,?,?)",
                 (str(tid), fullname, phone, prof_en, prof_uz, "pending", None))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"add_user error: {e}")
        return False

def get_user(tid):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE telegram_id=?", (str(tid),))
        r = c.fetchone()
        conn.close()
        return dict(r) if r else None
    except:
        return None

# Admin notification
async def notify_admin(bot, text):
    try:
        admin_id = int(os.getenv("ADMIN_ID", 0))
        if admin_id > 0:
            await bot.send_message(admin_id, text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"notify_admin error: {e}")

# ============= START COMMAND =============
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Ro'yxatdan o'tishni boshlash"""
    await state.clear()
    
    # Kontakt tugmasi bilan keyboard
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="👤 Ism-familiyani yuborish", request_contact=True)],
        [KeyboardButton(text="✍️ Qo'lda kiritish")]
    ], resize_keyboard=True, one_time_keyboard=True)
    
    await message.answer(
        "👋 <b>WorldSkills Shanghai 2026 ga xush kelibsiz!</b>\n\n"
        "📝 <b>1-qadam: Ism va familiyangizni kiriting:</b>\n"
        "<i>Masalan: Ali Valiyev</i>\n\n"
        "Yoki tugmani bosing:",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await state.set_state(RegisterState.fullname)

# ============= FULLNAME HANDLER =============
@router.message(RegisterState.fullname)
async def process_fullname(message: Message, state: FSMContext):
    """Ism-familiyani qabul qilish"""
    # Kontakt orqali kelganmi?
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
    
    # "Qo'lda kiritish" tugmasi bosilganmi?
    if message.text == "✍️ Qo'lda kiritish":
        await message.answer("📝 Ism va familiyangizni kiriting:\n<i>Masalan: Ali Valiyev</i>", parse_mode="HTML")
        return
    
    # Oddiy xabar - ism-familiya tekshiruvi
    fullname = message.text.strip()
    
    if not all(c.isalpha() or c.isspace() or c in "'-" for c in fullname):
        await message.answer("❌ <b>Ism-familiya faqat harflardan iborat bo'lishi kerak!</b>\n\nQaytadan kiriting:", parse_mode="HTML")
        return
    
    if len(fullname.split()) < 2:
        await message.answer("❌ <b>Ism va familiyangizni to'liq kiriting!</b>\n\nMasalan: Ali Valiyev\n\nQaytadan kiriting:", parse_mode="HTML")
        return
    
    await state.update_data(fullname=fullname)
    
    # Telefon so'rash
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📱 Telefon raqamimni yuborish", request_contact=True)],
        [KeyboardButton(text="✍️ Qo'lda kiritish")]
    ], resize_keyboard=True, one_time_keyboard=True)
    
    await message.answer(
        f"✅ <b>{fullname}</b>\n\n"
        f"📱 <b>2-qadam: Telefon raqamingizni kiriting:</b>\n"
        f"<i>Masalan: +998901234567</i>\n\n"
        f"Yoki tugmani bosing:",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await state.set_state(RegisterState.phone)

# ============= PHONE HANDLER =============
@router.message(RegisterState.phone)
async def process_phone(message: Message, state: FSMContext):
    """Telefon raqamni qabul qilish"""
    # Kontakt orqali kelganmi?
    if message.contact:
        phone = message.contact.phone_number
        user_data = await state.get_data()
        fullname = user_data.get("fullname")
        
        await show_categories(message, state, fullname, phone)
        return
    
    # "Qo'lda kiritish" tugmasi bosilganmi?
    if message.text == "✍️ Qo'lda kiritish":
        await message.answer("📱 Telefon raqamingizni kiriting:\n<i>Masalan: +998901234567</i>", parse_mode="HTML")
        return
    
    # Oddiy telefon raqami - validatsiya
    phone = message.text.strip().replace(" ", "").replace("-", "")
    
    if not re.match(r'^\+?998\d{9}$', phone):
        await message.answer(
            "❌ <b>Telefon raqami noto'g'ri!</b>\n\n"
            "<i>Masalan: +998901234567 yoki 998901234567</i>\n\n"
            "Qaytadan kiriting yoki tugmani bosing:",
            parse_mode="HTML"
        )
        return
    
    user_data = await state.get_data()
    fullname = user_data.get("fullname")
    
    await show_categories(message, state, fullname, phone)

# ============= SHOW CATEGORIES =============
async def show_categories(message: Message, state: FSMContext, fullname, phone):
    """6 ta kategoriya ko'rsatish"""
    
    categories = [
        ("🏭 Ishlab chiqarish | Manufacturing (17 ta)", "cat1"),
        ("💻 IT va Axborot | IT & Communication (8 ta)", "cat2"),
        ("🏗️ Qurilish | Construction (14 ta)", "cat3"),
        ("🚚 Transport va Logistika | Transport (8 ta)", "cat4"),
        ("🎨 San'at va Moda | Creative Arts (7 ta)", "cat5"),
        ("👥 Xizmatlar | Social Services (10 ta)", "cat6")
    ]
    
    builder = types.InlineKeyboardBuilder()
    for name, cat_id in categories:
        builder.button(text=name, callback_data=f"reg_cat_{cat_id}_{fullname}_{phone}")
    builder.adjust(1)
    
    await message.answer(
        "🎓 <b>3-qadam: Kategoriya tanlang | Choose category:</b>",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

# ============= CATEGORY CALLBACK =============
@router.callback_query(F.data.startswith("reg_cat_"))
async def callback_category(callback: types.CallbackQuery, state: FSMContext):
    """Kategoriya tanlangach kasblarni ko'rsatish"""
    parts = callback.data.split("_")
    if len(parts) < 5:
        await callback.answer("Xatolik", show_alert=True)
        return
    
    cat_id = parts[2]
    fullname = parts[3]
    phone = parts[4]
    
    # Kasblar bazasi (64 ta) - EN/UZ
    professions = {
        "cat1": [
            ("Industrial Mechanics | Sanoat mexanikasi", "p1_1"),
            ("Mechatronics | Mexatronika", "p1_2"),
            ("Mechanical Engineering CAD | Mexanik muhandislik CAD", "p1_3"),
            ("CNC Turning | CNC tokarlik", "p1_4"),
            ("CNC Milling | CNC frezalash", "p1_5"),
            ("Welding | Payvandlash", "p1_6"),
            ("Electronics | Elektronika", "p1_7"),
            ("Industrial Control | Sanoat boshqaruvi", "p1_8"),
            ("Mobile Robotics | Mobil robototexnika", "p1_9"),
            ("Industry 4.0 | Sanoat 4.0", "p1_10"),
            ("Chemical Laboratory | Kimyo laboratoriya", "p1_11"),
            ("Water Technology | Suv texnologiyasi", "p1_12"),
            ("3D Printing | 3D chop etish", "p1_13"),
            ("Industrial Design | Sanoat dizayni", "p1_14"),
            ("Optoelectronics | Optoelektronika", "p1_15"),
            ("Renewable Energy | Qayta energiya", "p1_16"),
            ("Robot Integration | Robot tizimlari", "p1_17")
        ],
        "cat2": [
            ("ICT Network | Tarmoq infratuzilmasi", "p2_1"),
            ("Mobile Apps | Mobil ilovalar", "p2_2"),
            ("Software Development | Dasturiy ta'minot", "p2_3"),
            ("Web Technologies | Veb texnologiyalar", "p2_4"),
            ("Network Admin | Tarmoq boshqaruvi", "p2_5"),
            ("Cloud Computing | Bulutli hisoblash", "p2_6"),
            ("Cyber Security | Kiberxavfsizlik", "p2_7"),
            ("Software Testing | Dasturiy sinov", "p2_8")
        ],
        "cat3": [
            ("Wall Tiling | Plitkalash", "p3_1"),
            ("Plumbing | Santexnika", "p3_2"),
            ("Electrical | Elektr o'rnatish", "p3_3"),
            ("Bricklaying | G'isht terish", "p3_4"),
            ("Plastering | Suvoq", "p3_5"),
            ("Painting | Bo'yash", "p3_6"),
            ("Cabinetmaking | Duradgorlik", "p3_7"),
            ("Joinery | Yig'ish ishlari", "p3_8"),
            ("Carpentry | Yog'och ishlari", "p3_9"),
            ("Landscape | Landshaft", "p3_10"),
            ("Refrigeration | Sovutish", "p3_11"),
            ("Concrete Work | Beton ishlari", "p3_12"),
            ("Digital Construction | Raqamli qurilish", "p3_13"),
            ("Security Tech | Xavfsizlik", "p3_14")
        ],
        "cat4": [
            ("Autobody Repair | Kuzov ta'mirlash", "p4_1"),
            ("Aircraft Maintenance | Samolyot xizmati", "p4_2"),
            ("Automobile Tech | Avtomobil", "p4_3"),
            ("Car Painting | Avtomobil bo'yash", "p4_4"),
            ("Heavy Vehicle | Og'ir transport", "p4_5"),
            ("Logistics | Logistika", "p4_6"),
            ("Rail Vehicle | Temiryo'l", "p4_7"),
            ("UAV Systems | Uchuvchisiz apparatlar", "p4_8")
        ],
        "cat5": [
            ("Jewellery | Zargarlik", "p5_1"),
            ("Floristry | Gulchilik", "p5_2"),
            ("Fashion Tech | Moda", "p5_3"),
            ("Graphic Design | Grafik dizayn", "p5_4"),
            ("Visual Merch | Vizual savdo", "p5_5"),
            ("3D Game Art | 3D o'yin san'ati", "p5_6"),
            ("Media Design | Media dizayn", "p5_7")
        ],
        "cat6": [
            ("Hairdressing | Sartaroshlik", "p6_1"),
            ("Beauty Therapy | Go'zallik", "p6_2"),
            ("Patisserie | Qandolatchilik", "p6_3"),
            ("Cooking | Oshpazlik", "p6_4"),
            ("Restaurant Service | Restoran", "p6_5"),
            ("Health Care | Sog'liqni saqlash", "p6_6"),
            ("Bakery | Nonvoychilik", "p6_7"),
            ("Hotel Reception | Mehmonxona", "p6_8"),
            ("Dental Prosthetics | Tish protezi", "p6_9"),
            ("Retail Sales | Savdo", "p6_10")
        ]
    }
    
    profs = professions.get(cat_id, [])
    if not profs:
        await callback.answer("Kasblar topilmadi", show_alert=True)
        return
    
    builder = types.InlineKeyboardBuilder()
    for name, prof_id in profs:
        safe_name = name.replace(" ", "_")[:40]
        builder.button(text=name, callback_data=f"reg_prof_{prof_id}_{safe_name}_{fullname}_{phone}_{cat_id}")
    builder.adjust(1)
    
    cat_names = {"cat1":"🏭 Ishlab chiqarish","cat2":"💻 IT","cat3":"🏗️ Qurilish",
                 "cat4":"🚚 Transport","cat5":"🎨 San'at","cat6":"👥 Xizmatlar"}
    
    await callback.message.answer(
        f"{cat_names.get(cat_id,'')} kasblari:\n\n"
        "Kasbingizni tanlang | Choose profession:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

# ============= PROFESSION CALLBACK =============
@router.callback_query(F.data.startswith("reg_prof_"))
async def callback_profession(callback: types.CallbackQuery, state: FSMContext):
    """Kasb tanlangach - ro'yxatdan o'tish tugallandi"""
    # Parse: reg_prof_p1_1_Industrial_Mechanics_Ali_Valiyev_998901234567_cat1
    parts = callback.data.split("_")
    if len(parts) < 7:
        await callback.answer("Xatolik", show_alert=True)
        return
    
    prof_id = parts[2]
    prof_name = "_".join(parts[3:-3])
    fullname = parts[-3]
    phone = parts[-2]
    cat_id = parts[-1]
    
    # Database'ga saqlash
    add_user(callback.from_user.id, fullname, phone, prof_name, prof_name)
    
    # Admin'ga xabar
    await notify_admin(callback.bot,
        f"🏆 <b>YANGI ISHTIROKCHI!</b>\n\n"
        f"👤 {fullname}\n"
        f"📱 {phone}\n"
        f"🔧 <b>Kasb:</b> {prof_name.replace('_', ' ')}\n"
        f"🆔 <code>{callback.from_user.id}</code>")
    
    # Tugmalar ko'rsatish
    builder = types.InlineKeyboardBuilder()
    builder.button(text="🤖 AI yordamchi", callback_data="menu_ai")
    builder.button(text="👨‍💼 Admin yordami", callback_data="menu_admin")
    builder.button(text="📄 Mening ma'lumotlarim", callback_data="menu_info")
    builder.button(text="🌐 Mini App ochish", web_app=WebAppInfo(url=os.getenv("WEBAPP_URL", "https://worldskills-bot.onrender.com")))
    builder.adjust(2)
    
    await callback.message.answer(
        f"✅ <b>Tabriklaymiz! Ro'yxatdan o'tdingiz!</b>\n\n"
        f"👤 <b>Ism:</b> {fullname}\n"
        f"📱 <b>Telefon:</b> {phone}\n"
        f"🔧 <b>Kasb:</b> {prof_name.replace('_', ' ')}\n\n"
        f"Endi bo'limni tanlang:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    
    await state.clear()
    await callback.answer()

# ============= MENU CALLBACKS =============
@router.callback_query(F.data == "menu_ai")
async def callback_ai(callback: types.CallbackQuery):
    await callback.message.answer(
        "🤖 <b>AI Yordamchi | AI Assistant</b>\n\n"
        "Savolingizni yozing, men yordam beraman!\n\n"
        "<i>Masalan:</i>\n"
        "• WorldSkills qachon bo'ladi?\n"
        "• Qanday hujjatlar kerak?\n"
        "• Tayyorgarlik bo'yicha maslahat",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "menu_admin")
async def callback_admin_help(callback: types.CallbackQuery):
    builder = types.InlineKeyboardBuilder()
    builder.button(text="📱 Telegram", url="https://t.me/worldskills_admin")
    builder.button(text="📞 Telefon", url="tel:+998933404080")
    builder.button(text="📧 Email", url="mailto:dadaxon45@gmail.com")
    builder.button(text="🌐 Web-sayt", url="https://worldskills.uz/ru")
    builder.adjust(2)
    
    await callback.message.answer(
        "👨‍💼 <b>Admin Yordami</b>\n\n"
        "📞 <b>Aloqa:</b>\n"
        "• Telegram: @worldskills_admin\n"
        "• Telefon: +998 93 340 40 80\n"
        "• Email: dadaxon45@gmail.com\n\n"
        "🌐 <b>Web-sayt:</b>\n"
        "• worldskills.uz",
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
            f"📊 <b>Status:</b> {user.get('status','pending')}\n"
            f"🆔 <b>ID:</b> <code>{user.get('telegram_id')}</code>",
            parse_mode="HTML"
        )
    else:
        await callback.message.answer("❌ Ma'lumot topilmadi")
    await callback.answer()
