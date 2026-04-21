# -*- coding: utf-8 -*-
from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, WebAppInfo
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
        "🏆 <b>WorldSkills Shanghai 2026</b>\n"
        "<i>48-chi Jahon Kasb Chempionati</i>\n\n"
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

# ============= SHOW CATEGORIES (6 ta) =============
async def show_categories(message: Message, state: FSMContext, fullname, phone):
    categories = [
        ("🏭 Ishlab chiqarish va Muhandislik (17 ta kasb)", "cat1"),
        ("💻 Axborot va Kommunikatsiya Texnologiyalari (8 ta kasb)", "cat2"),
        ("🏗️ Qurilish va Bino Texnologiyalari (14 ta kasb)", "cat3"),
        ("🚚 Transport va Logistika (8 ta kasb)", "cat4"),
        ("🎨 Ijodiy San'at va Moda (7 ta kasb)", "cat5"),
        ("👥 Ijtimoiy va Shaxsiy Xizmatlar (10 ta kasb)", "cat6")
    ]
    
    builder = InlineKeyboardBuilder()
    for name, cat_id in categories:
        builder.button(text=name, callback_data=f"reg_cat_{cat_id}|{fullname}|{phone}")
    builder.adjust(1)
    
    await message.answer(
        "🎓 <b>3-QADAM: Kategoriya tanlang</b>\n\n"
        "<i>64 ta kasbdan birini tanlang:</i>",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

# ============= CATEGORY CALLBACK (64 ta kasb) =============
@router.callback_query(F.data.startswith("reg_cat_"))
async def callback_category(callback: types.CallbackQuery, state: FSMContext):
    try:
        data = callback.data.replace("reg_cat_", "")
        parts = data.split("|")
        cat_id = parts[0]
        fullname = parts[1] if len(parts) > 1 else ""
        phone = parts[2] if len(parts) > 2 else ""
        
        # ALL 64 PROFESSIONS
        professions = {
            "cat1": [
                ("🏭 Industrial Mechanics | Sanoat mexanikasi", "p1_1"),
                ("⚙️ Mechatronics | Mexatronika", "p1_2"),
                ("📐 Mechanical Engineering CAD | Mexanik muhandislik CAD", "p1_3"),
                ("🔄 CNC Turning | CNC tokarlik", "p1_4"),
                ("🔧 CNC Milling | CNC frezalash", "p1_5"),
                ("🔥 Welding | Payvandlash", "p1_6"),
                ("🔌 Electronics | Elektronika", "p1_7"),
                ("🎛️ Industrial Control | Sanoat boshqaruvi", "p1_8"),
                ("🤖 Mobile Robotics | Mobil robototexnika", "p1_9"),
                ("🏭 Industry 4.0 | Sanoat 4.0", "p1_10"),
                ("🧪 Chemical Laboratory Technology | Kimyo laboratoriya", "p1_11"),
                ("💧 Water Technology | Suv texnologiyasi", "p1_12"),
                ("🖨️ Additive Manufacturing | 3D chop etish", "p1_13"),
                ("🎨 Industrial Design Technology | Sanoat dizayni", "p1_14"),
                ("💡 Optoelectronic Technology | Optoelektronika", "p1_15"),
                ("🌱 Renewable Energy | Qayta energiya", "p1_16"),
                ("🦾 Robot Systems Integration | Robot tizimlari", "p1_17")
            ],
            "cat2": [
                ("🌐 ICT Network Infrastructure | Tarmoq infratuzilmasi", "p2_1"),
                ("📱 Mobile Applications | Mobil ilovalar", "p2_2"),
                ("💻 Software Development | Dasturiy ta'minot", "p2_3"),
                ("🌍 Web Technologies | Veb texnologiyalar", "p2_4"),
                ("🖥️ IT Network Administration | Tarmoq boshqaruvi", "p2_5"),
                ("☁️ Cloud Computing | Bulutli hisoblash", "p2_6"),
                ("🔒 Cyber Security | Kiberxavfsizlik", "p2_7"),
                ("✅ Software Testing | Dasturiy sinov", "p2_8")
            ],
            "cat3": [
                ("🧱 Wall and Floor Tiling | Plitkalash", "p3_1"),
                ("🚿 Plumbing and Heating | Santexnika", "p3_2"),
                ("⚡ Electrical Installations | Elektr o'rnatish", "p3_3"),
                ("🧱 Bricklaying | G'isht terish", "p3_4"),
                ("🎨 Plastering | Suvoq", "p3_5"),
                ("🖌️ Painting | Bo'yash", "p3_6"),
                ("🪚 Cabinetmaking | Duradgorlik", "p3_7"),
                ("🔩 Joinery | Yig'ish ishlari", "p3_8"),
                ("🌲 Carpentry | Yog'och ishlari", "p3_9"),
                ("🌳 Landscape Gardening | Landshaft", "p3_10"),
                ("❄️ Refrigeration and Air Conditioning | Sovutish", "p3_11"),
                ("🏗️ Concrete Work | Beton ishlari", "p3_12"),
                ("📐 Digital Construction | Raqamli qurilish", "p3_13"),
                ("🔐 Security Technology | Xavfsizlik", "p3_14")
            ],
            "cat4": [
                ("🚗 Autobody Repair | Kuzov ta'mirlash", "p4_1"),
                ("✈️ Aircraft Maintenance | Samolyot xizmati", "p4_2"),
                ("🚙 Automobile Technology | Avtomobil", "p4_3"),
                ("🎨 Car Painting | Avtomobil bo'yash", "p4_4"),
                ("🚛 Heavy Vehicle | Og'ir transport", "p4_5"),
                ("📦 Logistics | Logistika", "p4_6"),
                ("🚆 Rail Vehicle Technology | Temiryo'l", "p4_7"),
                ("🚁 UAV Systems | Uchuvchisiz apparatlar", "p4_8")
            ],
            "cat5": [
                ("💎 Jewellery | Zargarlik", "p5_1"),
                ("🌸 Floristry | Gulchilik", "p5_2"),
                ("👗 Fashion Technology | Moda", "p5_3"),
                ("🎨 Graphic Design Technology | Grafik dizayn", "p5_4"),
                ("🛍️ Visual Merchandising | Vizual savdo", "p5_5"),
                ("🎮 3D Game Art | 3D o'yin san'ati", "p5_6"),
                ("📺 Media Design | Media dizayn", "p5_7")
            ],
            "cat6": [
                ("💇 Hairdressing | Sartaroshlik", "p6_1"),
                ("💆 Beauty Therapy | Go'zallik", "p6_2"),
                ("🍰 Patisserie and Confectionery | Qandolatchilik", "p6_3"),
                ("👨‍🍳 Cooking | Oshpazlik", "p6_4"),
                ("🍽️ Restaurant Service | Restoran", "p6_5"),
                ("🏥 Health and Social Care | Sog'liqni saqlash", "p6_6"),
                ("🍞 Bakery | Nonvoychilik", "p6_7"),
                ("🏨 Hotel Reception | Mehmonxona", "p6_8"),
                ("🦷 Dental Prosthetics | Tish protezi", "p6_9"),
                ("🛒 Retail Sales | Savdo", "p6_10")
            ]
        }
        
        profs = professions.get(cat_id, [])
        builder = InlineKeyboardBuilder()
        for name, prof_id in profs:
            builder.button(text=name, callback_data=f"reg_prof_{prof_id}|{fullname}|{phone}|{cat_id}")
        builder.adjust(1)
        
        cat_names = {
            "cat1": "🏭 Ishlab chiqarish",
            "cat2": "💻 IT va Axborot",
            "cat3": "🏗️ Qurilish",
            "cat4": "🚚 Transport",
            "cat5": "🎨 San'at",
            "cat6": "👥 Xizmatlar"
        }
        
        await callback.message.answer(
            f"{cat_names.get(cat_id,'')} kasblari:\n\n"
            "<i>Kasbingizni tanlang:</i>",
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
        
        prof_names = {
            "p1_1": "Industrial Mechanics | Sanoat mexanikasi",
            "p1_2": "Mechatronics | Mexatronika",
            "p1_3": "Mechanical Engineering CAD | Mexanik muhandislik CAD",
            "p1_4": "CNC Turning | CNC tokarlik",
            "p1_5": "CNC Milling | CNC frezalash",
            "p1_6": "Welding | Payvandlash",
            "p1_7": "Electronics | Elektronika",
            "p1_8": "Industrial Control | Sanoat boshqaruvi",
            "p1_9": "Mobile Robotics | Mobil robototexnika",
            "p1_10": "Industry 4.0 | Sanoat 4.0",
            "p1_11": "Chemical Laboratory | Kimyo laboratoriya",
            "p1_12": "Water Technology | Suv texnologiyasi",
            "p1_13": "Additive Manufacturing | 3D chop etish",
            "p1_14": "Industrial Design | Sanoat dizayni",
            "p1_15": "Optoelectronic Technology | Optoelektronika",
            "p1_16": "Renewable Energy | Qayta energiya",
            "p1_17": "Robot Systems Integration | Robot tizimlari",
            "p2_1": "ICT Network Infrastructure | Tarmoq infratuzilmasi",
            "p2_2": "Mobile Applications | Mobil ilovalar",
            "p2_3": "Software Development | Dasturiy ta'minot",
            "p2_4": "Web Technologies | Veb texnologiyalar",
            "p2_5": "IT Network Administration | Tarmoq boshqaruvi",
            "p2_6": "Cloud Computing | Bulutli hisoblash",
            "p2_7": "Cyber Security | Kiberxavfsizlik",
            "p2_8": "Software Testing | Dasturiy sinov",
            "p3_1": "Wall and Floor Tiling | Plitkalash",
            "p3_2": "Plumbing and Heating | Santexnika",
            "p3_3": "Electrical Installations | Elektr o'rnatish",
            "p3_4": "Bricklaying | G'isht terish",
            "p3_5": "Plastering | Suvoq",
            "p3_6": "Painting | Bo'yash",
            "p3_7": "Cabinetmaking | Duradgorlik",
            "p3_8": "Joinery | Yig'ish ishlari",
            "p3_9": "Carpentry | Yog'och ishlari",
            "p3_10": "Landscape Gardening | Landshaft",
            "p3_11": "Refrigeration | Sovutish",
            "p3_12": "Concrete Work | Beton ishlari",
            "p3_13": "Digital Construction | Raqamli qurilish",
            "p3_14": "Security Technology | Xavfsizlik",
            "p4_1": "Autobody Repair | Kuzov ta'mirlash",
            "p4_2": "Aircraft Maintenance | Samolyot xizmati",
            "p4_3": "Automobile Technology | Avtomobil",
            "p4_4": "Car Painting | Avtomobil bo'yash",
            "p4_5": "Heavy Vehicle | Og'ir transport",
            "p4_6": "Logistics | Logistika",
            "p4_7": "Rail Vehicle Technology | Temiryo'l",
            "p4_8": "UAV Systems | Uchuvchisiz apparatlar",
            "p5_1": "Jewellery | Zargarlik",
            "p5_2": "Floristry | Gulchilik",
            "p5_3": "Fashion Technology | Moda",
            "p5_4": "Graphic Design Technology | Grafik dizayn",
            "p5_5": "Visual Merchandising | Vizual savdo",
            "p5_6": "3D Game Art | 3D o'yin san'ati",
            "p5_7": "Media Design | Media dizayn",
            "p6_1": "Hairdressing | Sartaroshlik",
            "p6_2": "Beauty Therapy | Go'zallik",
            "p6_3": "Patisserie and Confectionery | Qandolatchilik",
            "p6_4": "Cooking | Oshpazlik",
            "p6_5": "Restaurant Service | Restoran",
            "p6_6": "Health and Social Care | Sog'liqni saqlash",
            "p6_7": "Bakery | Nonvoychilik",
            "p6_8": "Hotel Reception | Mehmonxona",
            "p6_9": "Dental Prosthetics | Tish protezi",
            "p6_10": "Retail Sales | Savdo"
        }
        prof_name = prof_names.get(prof_id, prof_id)
        
        add_user(callback.from_user.id, fullname, phone, prof_name, prof_name)
        
        await notify_admin(callback.bot,
            f"🏆 <b>YANGI ISHTIROKCHI RO'YXATDAN O'TDI!</b>\n\n"
            f"👤 <b>Ism:</b> {fullname}\n"
            f"📱 <b>Telefon:</b> {phone}\n"
            f"🔧 <b>Kasb:</b> {prof_name}\n"
            f"🆔 <b>ID:</b> <code>{callback.from_user.id}</code>\n\n"
            f"📅 {callback.message.date.strftime('%Y-%m-%d %H:%M:%S')}"
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
        builder.button(text="👨‍ Admin yordami", callback_data="menu_admin")
        builder.button(text="📄 Mening ma'lumotlarim", callback_data="menu_info")
        
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
    # Inline keyboard - faqat https URL'lar ishlaydi
    builder = InlineKeyboardBuilder()
    builder.button(text="📱 Telegram", url="https://t.me/worldskills_admin")
    builder.button(text="🌐 Web-sayt", url="https://worldskills.uz/ru")
    builder.button(text="📘 Facebook", url="https://www.facebook.com/WorldskillsUzbekistan/")
    builder.adjust(2)
    
    await callback.message.answer(
        "👨‍💼 <b>Admin Yordami</b>\n\n"
        "📞 <b>Aloqa:</b>\n"
        "• Telegram: @worldskills_admin\n"
        "• Telefon: <code>+998 93 340 40 80</code> 📋 (nusxalash uchun bosing)\n"
        "• Email: dadaxon45@gmail.com\n\n"
        "<i>Telefon raqamini nusxalash uchun ustiga bosing!</i>",
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
        await callback.message.answer("❌ Ma'lumot topilmadi. /start orqali ro'yxatdan o'ting.")
    await callback.answer()

@router.callback_query(F.data == "menu_admin")
async def callback_admin_help(callback: types.CallbackQuery):
    # Inline keyboard - faqat https URL'lar ishlaydi
    builder = InlineKeyboardBuilder()
    builder.button(text="📱 Telegram", url="https://t.me/worldskills_admin")
    builder.button(text="🌐 Web-sayt", url="https://worldskills.uz/ru")
    builder.button(text="📘 Facebook", url="https://www.facebook.com/WorldskillsUzbekistan/")
    builder.adjust(2)
    
    await callback.message.answer(
        "👨‍💼 <b>Admin Yordami</b>\n\n"
        "📞 <b>Aloqa:</b>\n"
        "• Telegram: @worldskills_admin\n"
        "• Telefon: <code>+998 93 340 40 80</code> 📋 (nusxalash uchun bosing)\n"
        "• Email: dadaxon45@gmail.com\n\n"
        "<i>Telefon raqamini nusxalash uchun ustiga bosing!</i>",
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
        await callback.message.answer("❌ Ma'lumot topilmadi. /start orqali ro'yxatdan o'ting.")
    await callback.answer()

@router.callback_query(F.data == "menu_admin")
async def callback_admin_help(callback: types.CallbackQuery):
    # Inline keyboard - faqat https URL'lar ishlaydi
    builder = InlineKeyboardBuilder()
    builder.button(text="📱 Telegram", url="https://t.me/worldskills_admin")
    builder.button(text="🌐 Web-sayt", url="https://worldskills.uz/ru")
    builder.button(text="📘 Facebook", url="https://www.facebook.com/WorldskillsUzbekistan/")
    builder.adjust(2)
    
    await callback.message.answer(
        "👨‍💼 <b>Admin Yordami</b>\n\n"
        "📞 <b>Aloqa:</b>\n"
        "• Telegram: @worldskills_admin\n"
        "• Telefon: <code>+998 93 340 40 80</code> 📋 (nusxalash uchun bosing)\n"
        "• Email: dadaxon45@gmail.com\n\n"
        "<i>Telefon raqamini nusxalash uchun ustiga bosing!</i>",
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
        await callback.message.answer("❌ Ma'lumot topilmadi. /start orqali ro'yxatdan o'ting.")
    await callback.answer()



