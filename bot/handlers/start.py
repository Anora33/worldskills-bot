# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from bot.config import WEBAPP_URL, ADMIN_ID, WORLDSKILLS_INFO, PROFESSION_MAP, CATEGORY_MAP, PROFESSIONS_BY_CATEGORY
from bot.database.db import get_user, add_user
import logging, asyncio, re

logger = logging.getLogger(__name__)
router = Router()

class UserState(StatesGroup):
    waiting_for_fullname = State()
    waiting_for_phone = State()
    waiting_for_category = State()
    waiting_for_profession = State()

# AI Yordamchi bilimlar bazasi
AI_KNOWLEDGE_BASE = {
    "worldskills": {
        "keywords": ["worldskills", "world skills", "chempionat", "musobaqa", "nima", "qanday"],
        "answer": """🏆 <b>WorldSkills</b> - bu jahon kasb mahorati chempionati!

📋 <b>Asosiy ma'lumotlar:</b>
• Yosh: 18-22 yoshli ishtirokchilar
• 64 ta turli kasb bo'yicha musobaqa
• Har 2 yilda bir marta o'tkaziladi
• 2026-yil Shanxayda (Xitoy) bo'lib o'tadi

🎯 <b>Maqsad:</b>
Yoshlarning kasbiy mahoratini oshirish va zamonaviy kasblarni rivojlantirish.

💡 <b>Qatnashish uchun:</b>
Mini App orqali ro'yxatdan o'ting va ishlaringizni yuklang!"""
    },
    "ro'yxatdan o'tish": {
        "keywords": ["ro'yxatdan o'tish", "qanday ro'yxatdan", "ishtirok", "qatnashish", "registratsiya"],
        "answer": """📝 <b>Ro'yxatdan o'tish jarayoni:</b>

1️⃣ <b>Mini App'ni oching</b> (pastdagi ko'k tugma)
2️⃣ <b>Ism va familiyangizni</b> kiriting
3️⃣ <b>Telefon raqamingizni</b> kiriting (+998 bilan)
4️⃣ <b>Kompetensiya kategoriyasini</b> tanlang
5️⃣ <b>Kasbingizni</b> tanlang

✅ Tayyor! Admin tasdiqlaydi va siz ishtirokchisiz!

📱 <b>Keyin:</b>
Ishlaringizni PDF formatda yuklang va natijalaringizni kuting!"""
    },
    "kasblar": {
        "keywords": ["kasb", "kompetensiya", "qaysi kasb", "yo'nalish", "specialty"],
        "answer": """🎓 <b>64 ta Kasb mavjud!</b>

🏭 <b>Ishlab chiqarish va Muhandislik (17):</b>
Sanoat mexanikasi, Mexatronika, CNC, Payvandlash, Robototexnika...

💻 <b>Axborot va Kommunikatsiya (8):</b>
Dasturlash, Veb texnologiyalar, Kiberxavfsizlik, Mobil ilovalar...

🏗️ <b>Qurilish (14):</b>
Elektr o'rnatish, Santexnika, G'isht terish, Bo'yash, Duradgorlik...

🚚 <b>Transport va Logistika (8):</b>
Avtomobil ta'mirlash, Samolyot xizmati, Logistika...

🎨 <b>Ijodiy San'at (7):</b>
Grafik dizayn, Moda, Zargarlik, Gulchilik...

👥 <b>Xizmatlar (10):</b>
Oshpazlik, Sartaroshlik, Go'zallik, Mehmonxona...

💡 Mini App'da batafsil ko'rib chiqing!"""
    },
    "pdf": {
        "keywords": ["pdf", "fayl", "yuklash", "portfolio", "ish", "hujjat"],
        "answer": """📄 <b>PDF Fayl Yuklash:</b>

✅ <b>Talablar:</b>
• Format: PDF
• Hajm: Max 10 MB
• Sifat: Aniq va o'qiladigan

📱 <b>Qanday yuklash:</b>
1. Mini App'ni oching
2. "Statistika" bo'limiga o'ting
3. "PDF faylni yuklash" tugmasini bosing
4. Faylni tanlang va yuklang

⏳ <b>Keyin nima bo'ladi:</b>
• Faylingiz admin tomonidan ko'rib chiqiladi
• Ball qo'yiladi (0-100)
• Natija statistika bo'limida ko'rinadi

💡 <b>Maslahat:</b>
Sifatli va to'liq ishlar yuklang - yuqori ball olish uchun!"""
    },
    "ball": {
        "keywords": ["ball", "baho", "natija", "reyting", "ochko"],
        "answer": """⭐ <b>Baholash Tizimi:</b>

📊 <b>Mezonlar:</b>
• Ish sifati: 40 ball
• Innovatsiya: 20 ball
• Texnik mahorat: 25 ball
• Taqdimot: 15 ball

🏆 <b>Natijalar:</b>
• 90-100 ball: A'lo (Oltin medal)
• 75-89 ball: Yaxshi (Kumush medal)
• 60-74 ball: Qoniqarli (Bronza medal)
• 0-59 ball: Tayyorgarlik kerak

📱 Natijalaringizni "Mening Natijalarim" bo'limida ko'ring!"""
    },
    "vaqt": {
        "keywords": ["qachon", "vaqt", "sana", "boshlanish", "muddat", "deadline"],
        "answer": """📅 <b>Muhim Sanalar:</b>

🎯 <b>2026-yil WorldSkills Shanghai:</b>
• Ro'yxatdan o'tish: Hozirdan boshlab
• Mintaqaviy bosqich: Tez orada e'lon qilinadi
• Milliy bosqich: 2026-yil boshi
• Xalqaro bosqich: 2026-yil sentyabr (Shanxay)

⏰ <b>Muddatlar:</b>
• Ishlarni yuklash: Doimiy
• Admin tekshiruvi: 3-5 kun
• Natijalar: Har hafta yangilanadi

📱 Yangiliklarni kuzatib boring!"""
    },
    "aloqa": {
        "keywords": ["aloqa", "telefon", "email", "bog'lanish", "savol", "yordam"],
        "answer": """📞 <b>Aloqa Ma'lumotlari:</b>

👨‍💼 <b>Admin Yordami:</b>
• Telegram: @worldskills_admin
• Telefon: +998 71 123 45 67
• Email: info@worldskills.uz

🕐 <b>Ish Vaqti:</b>
Dushanba - Juma: 9:00 - 18:00
Shanba - Yakshanba: Dam olish

💬 <b>Tezkor Javob:</b>
Savolingizni shu botga yozing - AI yordamchi darhol javob beradi!"""
    },
    "yutuq": {
        "keywords": ["yutuq", "mukofot", "medal", "sertifikat", "nima beriladi"],
        "answer": """🏆 <b>Yutuqlar va Mukofotlar:</b>

🥇 <b>G'oliblar:</b>
• Oltin medal + sertifikat
• Kumush medal + sertifikat  
• Bronza medal + sertifikat
• Medallion of Excellence (4-o'rin)

💰 <b>Qo'shimcha:</b>
• Xalqaro sertifikat
• Ish takliflari
• Grant imkoniyatlari
• Stajirovka imkoniyatlari

🌟 <b>Shuhrat:</b>
O'zbekiston nomini dunyoga tanitishingiz mumkin!"""
    }
}

async def notify_admin(bot, tid, fullname, profession, phone):
    try:
        await bot.send_message(
            ADMIN_ID,
            f"🔔 <b>🏆 YANGI ISHTIROKCHI!</b>\n\n"
            f"👤 <b>To'liq ism:</b> {fullname}\n"
            f"📱 <b>Telefon:</b> {phone}\n"
            f"🎓 <b>Kompetensiya:</b> {profession}\n"
            f"🆔 <b>ID:</b> <code>{tid}</code>\n"
            f"🌏 <b>Chempionat:</b> {WORLDSKILLS_INFO['name']}\n\n"
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
        timestamp = int(datetime.now().timestamp())
        
        # Menu button (Mini App)
        kb_menu = InlineKeyboardBuilder()
        kb_menu.button(
            text="🚀 Mini App'ni Ochish",
            web_app=WebAppInfo(url=f"{WEBAPP_URL}?t={timestamp}")
        )
        kb_menu.adjust(1)
        
        # Text keyboard
        keyboard = ReplyKeyboardBuilder()
        buttons = [
            "📊 Mening Natijalarim",
            "🏆 Musobaqalar",
            "🤖 AI Yordamchi",
            "📊 Reyting",
            "👨‍💼 Admin Yordami",
            "ℹ️ WorldSkills Haqida"
        ]
        for btn in buttons:
            keyboard.row(KeyboardButton(text=btn))
        
        await message.answer(
            f"🏆 <b>WorldSkills Uzbekistan</b>\n\n"
            f"👋 <b>Xush kelibsiz, {user.get('fullname')}!</b>\n\n"
            f"📊 <b>Sizning Profilingiz:</b>\n"
            f"• Kompetensiya: {user.get('profession')}\n"
            f"• Telefon: {user.get('phone')}\n"
            f"• Ball: {user.get('admin_score', 0)}/100\n\n"
            f"🌏 <b>{WORLDSKILLS_INFO['name']}</b>\n"
            f"<i>{WORLDSKILLS_INFO['edition']}</i>\n\n"
            f"<b>Mini App'ni ochish uchun pastdagi ko'k tugmani bosing:</b>",
            reply_markup=kb_menu.as_markup(),
            parse_mode="HTML"
        )
        
        await message.answer(
            "🎯 <b>Kerakli bo'limni tanlang:</b>",
            reply_markup=keyboard.as_markup(resize_keyboard=True),
            parse_mode="HTML"
        )
        return
    
    # Ro'yxatdan o'tmagan foydalanuvchi - Ism so'rash
    await state.clear()
    
    # Tugma bilan ism yuborish
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📱 Telefon raqamimni yuborish", request_contact=True))
    kb.row(KeyboardButton(text="✏️ Qo'lda kiritish"))
    
    await message.answer(
        f"🏆 <b>{WORLDSKILLS_INFO['name']}</b>\n\n"
        f"📝 <b>Ro'yxatdan o'tish</b>\n\n"
        f"<b>Ism va familiyangizni kiriting:</b>\n"
        f"<i>Masalan: Ali Valiyev</i>",
        reply_markup=kb.as_markup(resize_keyboard=True),
        parse_mode="HTML"
    )
    await state.set_state(UserState.waiting_for_fullname)

@router.message(UserState.waiting_for_fullname)
async def proc_name(msg: Message, state: FSMContext):
    # Agar kontakt bo'lsa
    if msg.contact:
        fullname = msg.contact.first_name
        if msg.contact.last_name:
            fullname += f" {msg.contact.last_name}"
    else:
        fullname = msg.text.strip()
    
    if len(fullname) < 3:
        await msg.answer("❌ <b>Ism juda qisqa!</b>\nIltimos, to'liq ism kiriting.", parse_mode="HTML")
        return
    
    await state.update_data(fullname=fullname)
    
    # Telefon raqam so'rash - tugma bilan
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📱 Telefon raqamimni yuborish", request_contact=True))
    kb.row(KeyboardButton(text="✏️ Qo'lda kiritish"))
    kb.row(KeyboardButton(text="🔙 Orqaga"))
    
    await msg.answer(
        f"✅ <b>{fullname}</b>\n\n"
        f"📱 <b>Telefon raqamingizni kiriting:</b>\n"
        f"<i>Masalan: +998 90 123 45 67</i>\n\n"
        f"<b>Yoki pastdagi tugmani bosing:</b>",
        reply_markup=kb.as_markup(resize_keyboard=True),
        parse_mode="HTML"
    )
    await state.set_state(UserState.waiting_for_phone)

@router.message(UserState.waiting_for_phone)
async def proc_phone(msg: Message, state: FSMContext):
    # Agar kontakt bo'lsa
    if msg.contact:
        phone = f"+{msg.contact.phone_number}"
    else:
        # Qo'lda kiritish
        phone = msg.text.strip()
    
    # Telefon raqamni tekshirish
    phone_clean = phone.replace(" ", "").replace("-", "")
    if not phone_clean.startswith("+") or len(phone_clean) < 12:
        await msg.answer(
            "❌ <b>Telefon noto'g'ri!</b>\n"
            "Iltimos, to'g'ri formatda kiriting:\n"
            "<i>+998 90 123 45 67</i>\n\n"
            "Yoki kontakt tugmasini bosing.",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(phone=phone)
    await state.set_state(UserState.waiting_for_category)
    
    # Kategoriya tanlash
    kb = InlineKeyboardBuilder()
    for cat_id, cat_name in CATEGORY_MAP.items():
        kb.button(text=cat_name, callback_data=cat_id)
    kb.adjust(1)
    kb.button(text="🔙 Orqaga", callback_data="back_to_name")
    
    await msg.answer(
        "✅ <b>Telefon qabul qilindi</b>\n\n"
        "🎓 <b>Kompetensiya kategoriyasini tanlang:</b>",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("cat_"))
async def select_category(cb: CallbackQuery, state: FSMContext):
    category_id = cb.data
    category_name = CATEGORY_MAP.get(category_id, "Noma'lum")
    await state.update_data(category_id=category_id, category_name=category_name)
    
    # Kasblarni ko'rsatish (EN + UZ)
    kb = InlineKeyboardBuilder()
    prof_ids = PROFESSIONS_BY_CATEGORY.get(category_id, [])
    
    for prof_id in prof_ids:
        prof_full = PROFESSION_MAP.get(prof_id, "Noma'lum")
        # Inglizcha va o'zbekcha ko'rsatish
        parts = prof_full.split(" | ")
        if len(parts) == 2:
            en_name = parts[0]
            uz_name = parts[1]
            display_text = f"{en_name}\n{uz_name}"
        else:
            display_text = prof_full
        
        kb.button(text=display_text, callback_data=prof_id)
    
    kb.adjust(1)
    kb.button(text="🔙 Kategoriyaga qaytish", callback_data="back_to_category")
    
    await cb.message.edit_text(
        f"🎓 <b>{category_name}</b>\n\n"
        f"<b>Kasbni tanlang (Ingliz + O'zbek):</b>",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )
    await cb.answer()

@router.callback_query(F.data.startswith("prof_"))
async def proc_prof(cb: CallbackQuery, state: FSMContext):
    prof_id = cb.data
    profession_full = PROFESSION_MAP.get(prof_id, "Noma'lum")
    
    d = await state.get_data()
    fullname = d.get("fullname", "")
    tid = cb.from_user.id
    phone = d.get("phone", "")
    
    add_user(tid, fullname, phone, profession_full, "uz")
    asyncio.create_task(notify_admin(cb.bot, tid, fullname, profession_full, phone))
    
    # Asosiy menyu - "WorldSkills App" O'CHIRILDI
    kb = ReplyKeyboardBuilder()
    buttons = [
        "📊 Mening Natijalarim",
        "🏆 Musobaqalar",
        "🤖 AI Yordamchi",
        "📊 Reyting",
        "👨‍💼 Admin Yordami",
        "ℹ️ WorldSkills Haqida"
    ]
    for btn in buttons:
        kb.row(KeyboardButton(text=btn))
    
    # Kasb nomini ko'rsatish
    parts = profession_full.split(" | ")
    display_prof = parts[1] if len(parts) == 2 else parts[0]
    
    await cb.message.answer(
        f"🎉 <b>Muvaffaqiyatli Ro'yxatdan O'tdingiz!</b>\n\n"
        f"✅ <b>Ma'lumotlaringiz qabul qilindi</b>\n"
        f"🎓 <b>Kompetensiya:</b> {display_prof}\n"
        f"🔔 <b>Admin xabardor qilindi</b>\n"
        f"🌏 <b>{WORLDSKILLS_INFO['name']}</b>\n\n"
        f"<i>Tasdiqlangandan so'ng SMS xabar yuboriladi</i>\n\n"
        f"🎯 <b>Mini App orqali ishlaringizni yuklang:</b>",
        reply_markup=kb.as_markup(resize_keyboard=True),
        parse_mode="HTML"
    )
    await cb.answer()

@router.callback_query(F.data == "back_to_category")
async def back_to_category(cb: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.waiting_for_category)
    kb = InlineKeyboardBuilder()
    for cat_id, cat_name in CATEGORY_MAP.items():
        kb.button(text=cat_name, callback_data=cat_id)
    kb.adjust(1)
    kb.button(text="🔙 Orqaga", callback_data="back_to_name")
    await cb.message.edit_text("🎓 <b>Kompetensiya kategoriyasini tanlang:</b>", reply_markup=kb.as_markup(), parse_mode="HTML")
    await cb.answer()

@router.callback_query(F.data == "back_to_name")
async def back_to_name(cb: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.waiting_for_phone)
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📱 Telefon raqamimni yuborish", request_contact=True))
    kb.row(KeyboardButton(text="✏️ Qo'lda kiritish"))
    await cb.message.answer("📱 <b>Telefon raqamingizni kiriting:</b>", reply_markup=kb.as_markup(resize_keyboard=True), parse_mode="HTML")
    await cb.answer()

# AI Yordamchi - Mukammal javoblar
@router.message(F.text == "🤖 AI Yordamchi")
async def ai_start(msg: Message, state: FSMContext):
    await state.update_data(ai_active=True)
    
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="🔙 Bosh Menyu"))
    
    await msg.answer(
        "🤖 <b>WorldSkills AI Yordamchisi</b>\n\n"
        "🎯 <b>Men sizga quyidagilarda yordam bera olaman:</b>\n\n"
        "• WorldSkills chempionati haqida\n"
        "• Ro'yxatdan o'tish jarayoni\n"
        "• 64 ta kasb haqida ma'lumot\n"
        "• PDF fayl yuklash\n"
        "• Ballar va natijalar\n"
        "• Muhim sanalar\n"
        "• Aloqa ma'lumotlari\n"
        "• Yutuqlar va mukofotlar\n\n"
        "<b>Savolingizni yozing:</b>\n"
        "<i>Masalan: \"WorldSkills nima?\" yoki \"Qanday ro'yxatdan o'taman?\"</i>",
        reply_markup=kb.as_markup(resize_keyboard=True),
        parse_mode="HTML"
    )

@router.message(F.text == "🔙 Bosh Menyu")
async def ai_exit(msg: Message, state: FSMContext):
    await state.update_data(ai_active=False)
    await state.clear()
    
    kb = ReplyKeyboardBuilder()
    buttons = [
        "📊 Mening Natijalarim",
        "🏆 Musobaqalar",
        "🤖 AI Yordamchi",
        "📊 Reyting",
        "👨‍💼 Admin Yordami",
        "ℹ️ WorldSkills Haqida"
    ]
    for btn in buttons:
        kb.row(KeyboardButton(text=btn))
    
    await msg.answer(
        "✅ <b>Bosh menyuga qaytdingiz</b>\n\n"
        "Kerakli bo'limni tanlang:",
        reply_markup=kb.as_markup(resize_keyboard=True),
        parse_mode="HTML"
    )

# AI Yordamchi - Savollarga javob berish
@router.message(lambda msg: True)
async def ai_answer(msg: Message, state: FSMContext):
    # Agar AI yordamchi aktiv bo'lsa
    data = await state.get_data()
    if not data.get("ai_active", False):
        return
    
    user_text = msg.text.lower()
    
    # AI bilimlar bazasidan qidirish
    best_match = None
    best_score = 0
    
    for topic, info in AI_KNOWLEDGE_BASE.items():
        for keyword in info["keywords"]:
            if keyword in user_text:
                score = len(keyword) / len(user_text)
                if score > best_score:
                    best_score = score
                    best_match = info["answer"]
    
    if best_match and best_score > 0.3:
        await msg.answer(best_match, parse_mode="HTML")
    else:
        # Agar topilmasa
        await msg.answer(
            "🤔 <b>Savolingizni to'liqroq yozing!</b>\n\n"
            "Men quyidagi mavzularda yordam bera olaman:\n\n"
            "• <b>WorldSkills</b> - chempionat haqida\n"
            "• <b>Ro'yxatdan o'tish</b> - qanday ishtirok etish\n"
            "• <b>Kasblar</b> - 64 ta yo'nalish\n"
            "• <b>PDF</b> - fayl yuklash\n"
            "• <b>Ball</b> - baholash tizimi\n"
            "• <b>Vaqt</b> - muhim sanalar\n"
            "• <b>Aloqa</b> - bog'lanish\n"
            "• <b>Yutuq</b> - mukofotlar\n\n"
            "<i>Masalan: \"WorldSkills nima?\" yoki \"Qanday ro'yxatdan o'taman?\"</i>",
            parse_mode="HTML"
        )

@router.message(F.text == "📊 Mening Natijalarim")
async def stats(msg: Message):
    user = get_user(msg.from_user.id)
    if user:
        status_emoji = {"pending":"⏳","approved":"✅","rejected":"❌"}.get(user.get("status"),"⏳")
        prof_parts = user.get('profession', '').split(' | ')
        prof_display = prof_parts[1] if len(prof_parts) == 2 else prof_parts[0]
        
        await msg.answer(
            f"📊 <b>Sizning Natijalaringiz</b>\n\n"
            f"👤 <b>To'liq ism:</b> {user.get('fullname')}\n"
            f"🎓 <b>Kompetensiya:</b> {prof_display}\n"
            f"📅 <b>Ro'yxatdan o'tgan:</b> {user.get('registered_at', 'Noma\\lum')}\n"
            f"📊 <b>Status:</b> {status_emoji} {user.get('status', 'pending').title()}\n"
            f"⭐ <b>Ball:</b> {user.get('admin_score', 0)}/100\n\n"
            f"<i>Mini App orqali ishlaringizni yuklang!</i>",
            parse_mode="HTML"
        )

@router.message(F.text == "🏆 Musobaqalar")
async def comp(msg: Message):
    await msg.answer(
        f"🏆 <b>{WORLDSKILLS_INFO['name']}</b>\n\n"
        f"📋 <b>{WORLDSKILLS_INFO['edition']}</b>\n"
        f"🔄 <b>Davriyligi:</b> {WORLDSKILLS_INFO['frequency']}\n\n"
        f"🏢 <b>Tashkilotchilar:</b>\n"
        f"• {WORLDSKILLS_INFO['organizers'][0]}\n"
        f"• {WORLDSKILLS_INFO['organizers'][1]}\n\n"
        f"📅 <b>Keyingi bosqichlar:</b>\n"
        f"• Mintaqaviy bosqich: Tez orada\n"
        f"• Milliy bosqich: Tez orada\n"
        f"• Xalqaro bosqich (Shanghai): 2026\n\n"
        f"<i>Ro'yxatdan o'tgan ishtirokchilarga SMS orqali xabar yuboriladi</i>",
        parse_mode="HTML"
    )

@router.message(F.text == "ℹ️ WorldSkills Haqida")
async def ws_info(msg: Message):
    await msg.answer(
        f"🏆 <b>{WORLDSKILLS_INFO['name']}</b>\n\n"
        f"📖 <b>Ta'rif:</b>\n{WORLDSKILLS_INFO['description']}\n\n"
        f"🌍 <b>Ahamiyati:</b>\n{WORLDSKILLS_INFO['significance']}\n\n"
        f"📋 <b>{WORLDSKILLS_INFO['edition']}</b>\n"
        f"🔄 <b>Davriyligi:</b> {WORLDSKILLS_INFO['frequency']}\n\n"
        f"🏢 <b>Tashkilotchilar:</b>\n"
        f"• {WORLDSKILLS_INFO['organizers'][0]}\n"
        f"• {WORLDSKILLS_INFO['organizers'][1]}\n\n"
        f"🎓 <b>64 ta Kompetensiya:</b>\n"
        f"• 🏭 Ishlab chiqarish va Muhandislik (17 ta)\n"
        f"• 💻 Axborot va Kommunikatsiya (8 ta)\n"
        f"• 🏗️ Qurilish va Bino Texnologiyalari (14 ta)\n"
        f"• 🚚 Transport va Logistika (8 ta)\n"
        f"• 🎨 Ijodiy San'at va Moda (7 ta)\n"
        f"• 👥 Ijtimoiy va Shaxsiy Xizmatlar (10 ta)\n\n"
        f"<i>Rivojlangan davlatlar ushbu chempionatga alohida e'tibor qaratadilar!</i>",
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
