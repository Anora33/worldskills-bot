# -*- coding: utf-8 -*-
from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
import sqlite3
import os

logger = logging.getLogger(__name__)
router = Router()

# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "worldskills.db")

# FSM States
class RegisterState(StatesGroup):
    fullname = State()
    phone = State()
    profession = State()

# Database helpers
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            telegram_id TEXT PRIMARY KEY,
            fullname TEXT,
            phone TEXT,
            profession TEXT,
            registered_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"DB init error: {e}")

def add_user(tid, fullname, phone, profession=""):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO users VALUES(?,?,?,?,?)",
                 (str(tid), fullname, phone, profession, None))
        conn.commit()
        conn.close()
        return True
    except:
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
    except:
        pass

# ============= START COMMAND =============
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Ro'yxatdan o'tishni boshlash"""
    await state.clear()
    
    # Kontakt tugmasi bilan keyboard
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="👤 Ism-familiyani yuborish", request_contact=True)]
    ], resize_keyboard=True, one_time_keyboard=True)
    
    await message.answer(
        "👋 <b>WorldSkills Shanghai 2026 ga xush kelibsiz!</b>\n\n"
        "📝 <b>Ism va familiyangizni kiriting:</b>\n"
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
        await show_profession_selection(message, state)
        return
    
    # Oddiy xabar - ism-familiya tekshiruvi
    fullname = message.text.strip()
    
    # Faqat harflar va bo'shliq
    if not all(c.isalpha() or c.isspace() or c in "'-" for c in fullname):
        await message.answer("❌ <b>Ism-familiya faqat harflardan iborat bo'lishi kerak!</b>\n\nQaytadan kiriting:", parse_mode="HTML")
        return
    
    # Kamida 2 ta so'z
    if len(fullname.split()) < 2:
        await message.answer("❌ <b>Ism va familiyangizni to'liq kiriting!</b>\n\nMasalan: Ali Valiyev\n\nQaytadan kiriting:", parse_mode="HTML")
        return
    
    await state.update_data(fullname=fullname)
    
    # Telefon so'rash
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📱 Telefon raqamimni yuborish", request_contact=True)]
    ], resize_keyboard=True, one_time_keyboard=True)
    
    await message.answer(
        f"✅ <b>{fullname}</b>\n\n"
        f"📱 <b>Telefon raqamingizni kiriting:</b>\n"
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
        
        # Database'ga saqlash
        add_user(message.from_user.id, fullname, phone)
        
        # Admin'ga xabar
        await notify_admin(message.bot, 
            f"🏆 <b>YANGI ISHTIROKCHI!</b>\n\n"
            f"👤 {fullname}\n"
            f"📱 {phone}\n"
            f"🆔 <code>{message.from_user.id}</code>")
        
        await message.answer("✅ Ro'yxatdan o'tdingiz!\n\n🎓 Endi kasbingizni tanlang:", 
                           reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")
        await show_profession_selection(message, state)
        return
    
    # Oddiy telefon raqami - validatsiya
    import re
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
    
    # Database'ga saqlash
    add_user(message.from_user.id, fullname, phone)
    
    # Admin'ga xabar
    await notify_admin(message.bot,
        f"🏆 <b>YANGI ISHTIROKCHI!</b>\n\n"
        f"👤 {fullname}\n"
        f"📱 {phone}\n"
        f"🆔 <code>{message.from_user.id}</code>")
    
    await message.answer("✅ Ro'yxatdan o'tdingiz!\n\n🎓 Endi kasbingizni tanlang:", 
                        reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")
    await show_profession_selection(message, state)

# ============= PROFESSION SELECTION =============
async def show_profession_selection(message: Message, state: FSMContext):
    """64 ta kasbni kategoriya bo'yicha ko'rsatish"""
    
    # Kategoriyalar
    categories = [
        ("🏭 Ishlab chiqarish", "cat1"),
        ("💻 IT va Axborot", "cat2"),
        ("🏗️ Qurilish", "cat3"),
        ("🚚 Transport", "cat4"),
        ("🎨 San'at va Moda", "cat5"),
        ("👥 Xizmatlar", "cat6")
    ]
    
    # Inline keyboard
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    for name, cat_id in categories:
        builder.button(text=name, callback_data=f"cat_{cat_id}")
    
    builder.adjust(2)
    
    await message.answer(
        "🎓 <b>Kasbingizni tanlang:</b>\n\n"
        "Kategoriyani tanlang, so'ng kasbingizni ko'rasiz:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await state.set_state(RegisterState.profession)

# ============= CATEGORY CALLBACK =============
@router.callback_query(F.data.startswith("cat_"))
async def callback_category(callback: types.CallbackQuery, state: FSMContext):
    """Kategoriya tanlangach kasblarni ko'rsatish"""
    cat_id = callback.data.replace("cat_", "")
    
    # Kasblar bazasi (64 ta)
    professions = {
        "cat1": [
            ("Industrial Mechanics", "Sanoat mexanikasi"),
            ("Mechatronics", "Mexatronika"),
            ("Mechanical Engineering CAD", "Mexanik muhandislik CAD"),
            ("CNC Turning", "CNC tokarlik"),
            ("CNC Milling", "CNC frezalash"),
            ("Welding", "Payvandlash"),
            ("Electronics", "Elektronika"),
            ("Industrial Control", "Sanoat boshqaruvi"),
            ("Mobile Robotics", "Mobil robototexnika"),
            ("Industry 4.0", "Sanoat 4.0"),
            ("Chemical Lab", "Kimyo laboratoriya"),
            ("Water Technology", "Suv texnologiyasi"),
            ("3D Printing", "3D chop etish"),
            ("Industrial Design", "Sanoat dizayni"),
            ("Optoelectronics", "Optoelektronika"),
            ("Renewable Energy", "Qayta energiya"),
            ("Robot Integration", "Robot tizimlari")
        ],
        "cat2": [
            ("ICT Network", "Tarmoq infratuzilmasi"),
            ("Mobile Apps", "Mobil ilovalar"),
            ("Software Dev", "Dasturiy ta'minot"),
            ("Web Technologies", "Veb texnologiyalar"),
            ("Network Admin", "Tarmoq boshqaruvi"),
            ("Cloud Computing", "Bulutli hisoblash"),
            ("Cyber Security", "Kiberxavfsizlik"),
            ("Software Testing", "Dasturiy sinov")
        ],
        "cat3": [
            ("Wall Tiling", "Plitkalash"),
            ("Plumbing", "Santexnika"),
            ("Electrical", "Elektr o'rnatish"),
            ("Bricklaying", "G'isht terish"),
            ("Plastering", "Suvoq"),
            ("Painting", "Bo'yash"),
            ("Cabinetmaking", "Duradgorlik"),
            ("Joinery", "Yig'ish ishlari"),
            ("Carpentry", "Yog'och ishlari"),
            ("Landscape", "Landshaft"),
            ("Refrigeration", "Sovutish"),
            ("Concrete Work", "Beton ishlari"),
            ("Digital Construction", "Raqamli qurilish"),
            ("Security Tech", "Xavfsizlik")
        ],
        "cat4": [
            ("Autobody Repair", "Kuzov ta'mirlash"),
            ("Aircraft Maint", "Samolyot xizmati"),
            ("Automobile Tech", "Avtomobil"),
            ("Car Painting", "Avtomobil bo'yash"),
            ("Heavy Vehicle", "Og'ir transport"),
            ("Logistics", "Logistika"),
            ("Rail Vehicle", "Temiryo'l"),
            ("UAV Systems", "Uchuvchisiz apparatlar")
        ],
        "cat5": [
            ("Jewellery", "Zargarlik"),
            ("Floristry", "Gulchilik"),
            ("Fashion Tech", "Moda"),
            ("Graphic Design", "Grafik dizayn"),
            ("Visual Merch", "Vizual savdo"),
            ("3D Game Art", "3D o'yin san'ati"),
            ("Media Design", "Media dizayn")
        ],
        "cat6": [
            ("Hairdressing", "Sartaroshlik"),
            ("Beauty Therapy", "Go'zallik"),
            ("Patisserie", "Qandolatchilik"),
            ("Cooking", "Oshpazlik"),
            ("Restaurant Svc", "Restoran"),
            ("Health Care", "Sog'liqni saqlash"),
            ("Bakery", "Nonvoychilik"),
            ("Hotel Reception", "Mehmonxona"),
            ("Dental Prosthetics", "Tish protezi"),
            ("Retail Sales", "Savdo")
        ]
    }
    
    profs = professions.get(cat_id, [])
    if not profs:
        await callback.answer("Kasblar topilmadi", show_alert=True)
        return
    
    # Inline keyboard for professions
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    for en_name, uz_name in profs:
        # Callback data max 64 chars
        safe_data = f"prof_{cat_id}_{en_name.replace(' ', '_')[:30]}"
        builder.button(text=f"{uz_name}", callback_data=safe_data)
    
    builder.adjust(1)
    
    cat_names = {"cat1":"🏭 Ishlab chiqarish","cat2":"💻 IT","cat3":"🏗️ Qurilish",
                 "cat4":"🚚 Transport","cat5":"🎨 San'at","cat6":"👥 Xizmatlar"}
    
    await callback.message.answer(
        f"{cat_names.get(cat_id,'')} kasblari:\n\n"
        "Kasbingizni tanlang:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

# ============= PROFESSION CALLBACK =============
@router.callback_query(F.data.startswith("prof_"))
async def callback_profession(callback: types.CallbackQuery, state: FSMContext):
    """Kasb tanlangach - admin'ga xabar"""
    # Parse callback data: prof_cat1_Industrial_Mechanics
    parts = callback.data.split("_")
    if len(parts) < 3:
        await callback.answer("Xatolik", show_alert=True)
        return
    
    cat_id = parts[1]
    prof_en = "_".join(parts[2:])
    
    # Kasb nomini uzga aylantirish
    prof_names = {
        "Industrial_Mechanics": "Sanoat mexanikasi",
        "Mechatronics": "Mexatronika",
        "Mechanical_Engineering_CAD": "Mexanik muhandislik CAD",
        "CNC_Turning": "CNC tokarlik",
        "CNC_Milling": "CNC frezalash",
        "Welding": "Payvandlash",
        "Electronics": "Elektronika",
        "Industrial_Control": "Sanoat boshqaruvi",
        "Mobile_Robotics": "Mobil robototexnika",
        "Industry_4_0": "Sanoat 4.0",
        "Chemical_Lab": "Kimyo laboratoriya",
        "Water_Technology": "Suv texnologiyasi",
        "3D_Printing": "3D chop etish",
        "Industrial_Design": "Sanoat dizayni",
        "Optoelectronics": "Optoelektronika",
        "Renewable_Energy": "Qayta energiya",
        "Robot_Integration": "Robot tizimlari",
        "ICT_Network": "Tarmoq infratuzilmasi",
        "Mobile_Apps": "Mobil ilovalar",
        "Software_Dev": "Dasturiy ta'minot",
        "Web_Technologies": "Veb texnologiyalar",
        "Network_Admin": "Tarmoq boshqaruvi",
        "Cloud_Computing": "Bulutli hisoblash",
        "Cyber_Security": "Kiberxavfsizlik",
        "Software_Testing": "Dasturiy sinov",
        "Wall_Tiling": "Plitkalash",
        "Plumbing": "Santexnika",
        "Electrical": "Elektr o'rnatish",
        "Bricklaying": "G'isht terish",
        "Plastering": "Suvoq",
        "Painting": "Bo'yash",
        "Cabinetmaking": "Duradgorlik",
        "Joinery": "Yig'ish ishlari",
        "Carpentry": "Yog'och ishlari",
        "Landscape": "Landshaft",
        "Refrigeration": "Sovutish",
        "Concrete_Work": "Beton ishlari",
        "Digital_Construction": "Raqamli qurilish",
        "Security_Tech": "Xavfsizlik",
        "Autobody_Repair": "Kuzov ta'mirlash",
        "Aircraft_Maint": "Samolyot xizmati",
        "Automobile_Tech": "Avtomobil",
        "Car_Painting": "Avtomobil bo'yash",
        "Heavy_Vehicle": "Og'ir transport",
        "Logistics": "Logistika",
        "Rail_Vehicle": "Temiryo'l",
        "UAV_Systems": "Uchuvchisiz apparatlar",
        "Jewellery": "Zargarlik",
        "Floristry": "Gulchilik",
        "Fashion_Tech": "Moda",
        "Graphic_Design": "Grafik dizayn",
        "Visual_Merch": "Vizual savdo",
        "3D_Game_Art": "3D o'yin san'ati",
        "Media_Design": "Media dizayn",
        "Hairdressing": "Sartaroshlik",
        "Beauty_Therapy": "Go'zallik",
        "Patisserie": "Qandolatchilik",
        "Cooking": "Oshpazlik",
        "Restaurant_Svc": "Restoran",
        "Health_Care": "Sog'liqni saqlash",
        "Bakery": "Nonvoychilik",
        "Hotel_Reception": "Mehmonxona",
        "Dental_Prosthetics": "Tish protezi",
        "Retail_Sales": "Savdo"
    }
    
    prof_uz = prof_names.get(prof_en, prof_en.replace("_", " "))
    
    # Database'ga kasbni saqlash
    user_data = await state.get_data()
    fullname = user_data.get("fullname", "Noma'lum")
    phone = user_data.get("phone", "Noma'lum")
    
    add_user(callback.from_user.id, fullname, phone, prof_uz)
    
    # Admin'ga xabar
    await notify_admin(callback.bot,
        f"🎓 <b>KASB TANLANDI!</b>\n\n"
        f"👤 {fullname}\n"
        f"📱 {phone}\n"
        f"🔧 <b>Kasb:</b> {prof_uz}\n"
        f"🆔 <code>{callback.from_user.id}</code>")
    
    # Foydalanuvchiga javob
    await callback.message.answer(
        f"✅ <b>{prof_uz}</b> kasbi tanlandi!\n\n"
        f"🤖 Endi AI yordamchidan foydalanishingiz mumkin:\n"
        f"/ai - Sun'iy intellekt bilan suhbat\n\n"
        f"👨‍💼 Savollaringiz bo'lsa:\n"
        f"/admin - Admin bilan bog'lanish",
        parse_mode="HTML"
    )
    
    await state.clear()
    await callback.answer()
