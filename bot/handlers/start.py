# -*- coding: utf-8 -*-
from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

# ========== STATE DEFINITIONS ==========
class RegistrationState(StatesGroup):
    waiting_for_fullname = State()
    waiting_for_phone = State()
    waiting_for_profession = State()

# ========== KEYBOARD FUNCTIONS ==========
def get_language_keyboard():
    """Til tanlash uchun inline keyboard"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺 O'zbekcha", callback_data="lang_uz")
    builder.button(text="🇷🇺 Русский", callback_data="lang_ru")
    builder.button(text="🇬🇧 English", callback_data="lang_en")
    builder.adjust(1)
    return builder.as_markup()

def get_profession_keyboard():
    """Kasb tanlash uchun inline keyboard"""
    builder = InlineKeyboardBuilder()
    builder.button(text="💻 Dasturlash", callback_data="prof_programming")
    builder.button(text="🎨 Dizayn", callback_data="prof_design")
    builder.button(text="🔧 Mexanika", callback_data="prof_mechanics")
    builder.button(text="🏗 Qurilish", callback_data="prof_construction")
    builder.button(text="👨‍ Oshpazlik", callback_data="prof_cooking")
    builder.button(text="💼 Biznes", callback_data="prof_business")
    builder.adjust(2)
    return builder.as_markup()

def get_main_menu_keyboard(lang="uz"):
    """Asosiy menyu - faqat ro'yxatdan o'tgandan keyin"""
    texts = {
        "uz": {
            "mini_app": "📱 Mini App",
            "my_stats": "📊 Mening statistikam",
            "schedule": "📅 Jadval",
            "my_competition": "🏆 Mening musobaqam",
            "ai_assistant": "🤖 AI yordamchi",
            "rating": "⭐ Reyting",
            "admin_help": "👨‍💼 Admin yordami",
            "change_profession": "🔄 Kasbni o'zgartirish"
        },
        "ru": {
            "mini_app": "📱 Mini App",
            "my_stats": "📊 Моя статистика",
            "schedule": "📅 Расписание",
            "my_competition": "🏆 Моё соревнование",
            "ai_assistant": "🤖 AI помощник",
            "rating": "⭐ Рейтинг",
            "admin_help": "👨‍💼 Помощь админа",
            "change_profession": "🔄 Сменить профессию"
        },
        "en": {
            "mini_app": "📱 Mini App",
            "my_stats": "📊 My statistics",
            "schedule": "📅 Schedule",
            "my_competition": "🏆 My competition",
            "ai_assistant": "🤖 AI assistant",
            "rating": "⭐ Rating",
            "admin_help": "👨‍💼 Admin help",
            "change_profession": "🔄 Change profession"
        }
    }
    
    t = texts.get(lang, texts["uz"])
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=t["mini_app"]))
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
    builder.row(KeyboardButton(text=t["change_profession"]))
    return builder.as_markup(resize_keyboard=True)

# ========== HANDLERS ==========

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """1-QADAM: Til tanlash"""
    await state.clear()
    await message.answer(
        "🌍 <b>Xush kelibsiz! / Welcome! / Добро пожаловать!</b>\n\n"
        "Botdan foydalanish uchun tilni tanlang:\n"
        "Choose language to continue:\n"
        "Выберите язык:",
        reply_markup=get_language_keyboard()
    )

@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery, state: FSMContext):
    """2-QADAM: Til tanlandi - ro'yxatdan o'tishga o'tish"""
    lang = callback.data.split("_")[1]
    
    # Tilni state'da saqlash
    await state.update_data(language=lang)
    
    texts = {
        "uz": "🇺🇿 O'zbek tili tanlandi!",
        "ru": "🇷🇺 Русский язык выбран!",
        "en": "🇬🇧 English selected!"
    }
    
    await callback.message.answer(
        f"{texts.get(lang, texts['uz'])}\n\n"
        "<b>Endi ro'yxatdan o'tamiz!</b>\n"
        "<b>Теперь зарегистрируемся!</b>\n"
        "<b>Now let's register!</b>\n\n"
        "<i>Ismingiz va familiyangizni kiriting:</i>\n"
        "<i>Введите ваше имя и фамилию:</i>\n"
        "<i>Enter your full name:</i>"
    )
    
    # Ro'yxatdan o'tish state'iga o'tish
    await state.set_state(RegistrationState.waiting_for_fullname)
    await callback.answer()

@router.message(RegistrationState.waiting_for_fullname)
async def process_fullname(message: Message, state: FSMContext):
    """3-QADAM: Ism familiya qabul qilish"""
    fullname = message.text.strip()
    
    if len(fullname) < 3:
        await message.answer(
            "❌ <b>Ism familiya juda qisqa!</b>\n"
            "Iltimos to'liq ism familiyangizni kiriting:\n\n"
            "Например: Ali Valiyev"
        )
        return
    
    await state.update_data(fullname=fullname)
    await state.set_state(RegistrationState.waiting_for_phone)
    
    await message.answer(
        f"✅ <b>Ism familiya: {fullname}</b>\n\n"
        "<b>Telefon raqamingizni kiriting:</b>\n"
        "<b>Введите номер телефона:</b>\n"
        "<i>Masalan: +998901234567</i>"
    )

@router.message(RegistrationState.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """4-QADAM: Telefon raqam qabul qilish"""
    phone = message.text.strip()
    
    # Telefon raqamni tekshirish
    if not phone.startswith("+") or len(phone) < 12:
        await message.answer(
            "❌ <b>Telefon raqam noto'g'ri!</b>\n\n"
            "Iltimos to'g'ri formatda kiriting:\n"
            "<i>Masalan: +998901234567</i>"
        )
        return
    
    await state.update_data(phone=phone)
    await state.set_state(RegistrationState.waiting_for_profession)
    
    await message.answer(
        f"✅ <b>Telefon: {phone}</b>\n\n"
        "<b>Kasbingizni tanlang:</b>\n"
        "<b>Выберите профессию:</b>",
        reply_markup=get_profession_keyboard()
    )

@router.callback_query(RegistrationState.waiting_for_profession)
async def process_profession(callback: CallbackQuery, state: FSMContext):
    """5-QADAM: Kasb tanlash - ro'yxatdan o'tish tugadi"""
    profession = callback.data.replace("prof_", "")
    
    # State'dan ma'lumotlarni olish
    user_data = await state.get_data()
    fullname = user_data.get("fullname")
    phone = user_data.get("phone")
    lang = user_data.get("language", "uz")
    
    # Bu yerda database'ga saqlash mumkin
    # await create_user(telegram_id=callback.from_user.id, fullname=fullname, phone=phone, profession=profession)
    
    await state.clear()
    
    texts = {
        "uz": f"🎉 <b>Tabriklaymiz, {fullname}!</b>\n\nRo'yxatdan o'tish muvaffaqiyatli yakunlandi!\n\nKasb: {profession}\nTelefon: {phone}\n\nEndi asosiy menyudan foydalanishingiz mumkin:",
        "ru": f"🎉 <b>Поздравляем, {fullname}!</b>\n\nРегистрация успешно завершена!\n\nПрофессия: {profession}\nТелефон: {phone}\n\nТеперь вы можете использовать основное меню:",
        "en": f"🎉 <b>Congratulations, {fullname}!</b>\n\nRegistration completed successfully!\n\nProfession: {profession}\nPhone: {phone}\n\nNow you can use the main menu:"
    }
    
    await callback.message.answer(
        texts.get(lang, texts["uz"]),
        reply_markup=get_main_menu_keyboard(lang)
    )
    await callback.answer()

# ========== ASOSIY MENYU TUGMALARI ==========

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

@router.message(F.text == "📊 Mening statistikam" or F.text == "📊 Моя статистика" or F.text == "📊 My statistics")
async def handle_stats(message: Message):
    await message.answer(
        "📊 <b>Mening Statistikam</b>\n\n"
        "📝 Topshiriqlar: 0/10\n"
        "✅ To'g'ri javoblar: 0\n"
        "❌ Noto'g'ri javoblar: 0\n"
        "🏆 Ball: 0\n\n"
        "<i>Tez orada ma'lumotlar qo'shiladi...</i>"
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
        "Sizning ma'lumotlaringiz yuklanmoqda...\n\n"
        "<i>Tez orada ko'rinadi</i>"
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

@router.message(F.text == "🔄 Kasbni o'zgartirish" or F.text == "🔄 Сменить профессию" or F.text == "🔄 Change profession")
async def handle_change_profession(message: Message, state: FSMContext):
    """Kasbni qayta tanlash"""
    await state.set_state(RegistrationState.waiting_for_profession)
    await message.answer(
        "<b>Yangi kasbingizni tanlang:</b>",
        reply_markup=get_profession_keyboard()
    )
