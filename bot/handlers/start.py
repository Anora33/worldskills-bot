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
class UserState(StatesGroup):
    waiting_for_fullname = State()
    waiting_for_phone = State()
    waiting_for_profession = State()
    ai_mode = State()

# ========== KEYBOARD FUNCTIONS ==========
def get_language_keyboard():
    """Til tanlash uchun inline keyboard"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbekcha", callback_data="lang_uz")
    builder.button(text="🇷🇺 Русский", callback_data="lang_ru")
    builder.button(text="🇬🇧 English", callback_data="lang_en")
    builder.adjust(1)
    return builder.as_markup()

def get_profession_keyboard(lang):
    """Kasb tanlash uchun inline keyboard"""
    texts = {
        "uz": ["💻 Dasturlash", "🎨 Dizayn", "🔧 Mexanika", "🏗 Qurilish", "👨‍🍳 Oshpazlik", "💼 Biznes"],
        "ru": ["💻 Программирование", "🎨 Дизайн", "🔧 Механика", "🏗 Строительство", "👨‍🍳 Кулинария", "💼 Бизнес"],
        "en": ["💻 Programming", "🎨 Design", "🔧 Mechanics", "🏗 Construction", "👨‍🍳 Cooking", "💼 Business"]
    }
    builder = InlineKeyboardBuilder()
    for btn in texts.get(lang, texts["uz"]):
        callback = btn.split()[-1].lower()
        builder.button(text=btn, callback_data=f"prof_{callback}")
    builder.adjust(2)
    return builder.as_markup()

def get_main_menu_keyboard(lang):
    """Asosiy menyu - faqat ro'yxatdan o'tgandan keyin"""
    texts = {
        "uz": {
            "mini_app": "📱 Mini App",
            "my_stats": "📊 Mening statistikam",
            "my_competition": "🏆 Mening musobaqam",
            "ai_assistant": "🤖 AI yordamchi",
            "rating": "⭐ Reyting",
            "admin_help": "👨‍💼 Admin yordami",
            "change_profession": "🔄 Kasbni o'zgartirish"
        },
        "ru": {
            "mini_app": "📱 Mini App",
            "my_stats": "📊 Моя статистика",
            "my_competition": "🏆 Моё соревнование",
            "ai_assistant": "🤖 AI помощник",
            "rating": "⭐ Рейтинг",
            "admin_help": "👨‍💼 Помощь админа",
            "change_profession": "🔄 Сменить профессию"
        },
        "en": {
            "mini_app": "📱 Mini App",
            "my_stats": "📊 My statistics",
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

# ========== TRANSLATIONS ==========
def t(key, lang):
    """Translation helper"""
    translations = {
        "welcome": {
            "uz": "🌍 <b>Xush kelibsiz!</b>\n\nBotdan foydalanish uchun tilni tanlang:",
            "ru": "🌍 <b>Добро пожаловать!</b>\n\nВыберите язык для использования бота:",
            "en": "🌍 <b>Welcome!</b>\n\nChoose a language to use the bot:"
        },
        "lang_selected": {
            "uz": "🇺🇿 O'zbek tili tanlandi!\n\n<b>Endi ro'yxatdan o'tamiz!</b>\n\n<i>Ismingiz va familiyangizni kiriting:</i>",
            "ru": "🇷🇺 Русский язык выбран!\n\n<b>Теперь зарегистрируемся!</b>\n\n<i>Введите ваше имя и фамилию:</i>",
            "en": "🇬🇧 English selected!\n\n<b>Now let's register!</b>\n\n<i>Enter your full name:</i>"
        },
        "invalid_name": {
            "uz": "❌ <b>Ism familiya juda qisqa!</b>\n\nIltimos to'liq ism familiyangizni kiriting:",
            "ru": "❌ <b>Имя слишком короткое!</b>\n\nПожалуйста, введите полное имя и фамилию:",
            "en": "❌ <b>Name too short!</b>\n\nPlease enter your full name:"
        },
        "enter_phone": {
            "uz": "✅ <b>Ism familiya: {name}</b>\n\n<b>Telefon raqamingizni kiriting:</b>\n<i>Masalan: +998901234567</i>",
            "ru": "✅ <b>Имя: {name}</b>\n\n<b>Введите номер телефона:</b>\n<i>Например: +998901234567</i>",
            "en": "✅ <b>Name: {name}</b>\n\n<b>Enter your phone number:</b>\n<i>Example: +998901234567</i>"
        },
        "invalid_phone": {
            "uz": "❌ <b>Telefon raqam noto'g'ri!</b>\n\nIltimos to'g'ri formatda kiriting:\n<i>Masalan: +998901234567</i>",
            "ru": "❌ <b>Неверный номер телефона!</b>\n\nПожалуйста, введите в правильном формате:\n<i>Например: +998901234567</i>",
            "en": "❌ <b>Invalid phone number!</b>\n\nPlease enter in correct format:\n<i>Example: +998901234567</i>"
        },
        "select_profession": {
            "uz": "✅ <b>Telefon: {phone}</b>\n\n<b>Kasbingizni tanlang:</b>",
            "ru": "✅ <b>Телефон: {phone}</b>\n\n<b>Выберите профессию:</b>",
            "en": "✅ <b>Phone: {phone}</b>\n\n<b>Select your profession:</b>"
        },
        "registration_complete": {
            "uz": "🎉 <b>Tabriklaymiz, {name}!</b>\n\nRo'yxatdan o'tish muvaffaqiyatli yakunlandi!\n\nKasb: {prof}\nTelefon: {phone}\n\nEndi asosiy menyudan foydalanishingiz mumkin:",
            "ru": "🎉 <b>Поздравляем, {name}!</b>\n\nРегистрация успешно завершена!\n\nПрофессия: {prof}\nТелефон: {phone}\n\nТеперь вы можете использовать основное меню:",
            "en": "🎉 <b>Congratulations, {name}!</b>\n\nRegistration completed successfully!\n\nProfession: {prof}\nPhone: {phone}\n\nNow you can use the main menu:"
        },
        "ai_welcome": {
            "uz": "🤖 <b>AI Yordamchi</b>\n\nSalom! Men sizga yordam berishga tayyorman.\n\nMenga savol bering:\n- Musobaqa haqida\n- Topshiriqlar haqida\n- Texnik yordam\n\n<i>Savolingizni yozing, men javob beraman!</i>\n\n<i>Chiqish uchun /start bosing</i>",
            "ru": "🤖 <b>AI Помощник</b>\n\nПривет! Я готов помочь вам.\n\nЗадайте мне вопрос:\n- О соревновании\n- О заданиях\n- Техническая помощь\n\n<i>Напишите ваш вопрос, я отвечу!</i>\n\n<i>Для выхода нажмите /start</i>",
            "en": "🤖 <b>AI Assistant</b>\n\nHello! I'm ready to help you.\n\nAsk me anything:\n- About the competition\n- About tasks\n- Technical support\n\n<i>Type your question, I'll answer!</i>\n\n<i>Type /start to exit</i>"
        },
        "ai_error": {
            "uz": "❌ AI vaqtincha ishlamayapti. Qayta urinib ko'ring.",
            "ru": "❌ AI временно не работает. Попробуйте позже.",
            "en": "❌ AI is temporarily unavailable. Please try again later."
        },
        "stats": {
            "uz": "📊 <b>Mening Statistikam</b>\n\n📝 Topshiriqlar: 0/10\n✅ To'g'ri javoblar: 0\n❌ Noto'g'ri javoblar: 0\n🏆 Ball: 0\n\n<i>Tez orada ma'lumotlar qo'shiladi...</i>",
            "ru": "📊 <b>Моя статистика</b>\n\n📝 Задания: 0/10\n✅ Правильные ответы: 0\n❌ Неправильные ответы: 0\n🏆 Баллы: 0\n\n<i>Скоро данные будут добавлены...</i>",
            "en": "📊 <b>My Statistics</b>\n\n📝 Tasks: 0/10\n✅ Correct answers: 0\n❌ Wrong answers: 0\n🏆 Score: 0\n\n<i>Data will be added soon...</i>"
        },
        "competition": {
            "uz": "🏆 <b>Mening Musobaqam</b>\n\nSizning ma'lumotlaringiz yuklanmoqda...\n\n<i>Tez orada ko'rinadi</i>",
            "ru": "🏆 <b>Моё соревнование</b>\n\nВаши данные загружаются...\n\n<i>Скоро будет видно</i>",
            "en": "🏆 <b>My Competition</b>\n\nYour data is loading...\n\n<i>Will be available soon</i>"
        },
        "rating": {
            "uz": "⭐ <b>Reyting</b>\n\n🏆 <b>Top 10 ishtirokchilar:</b>\n\n1. Ahmadjonov Ali - 950 ball\n2. Valiyeva Zebo - 920 ball\n3. Karimov Bobur - 890 ball\n\n<i>Tez orada to'liq reyting qo'shiladi...</i>",
            "ru": "⭐ <b>Рейтинг</b>\n\n🏆 <b>Топ 10 участников:</b>\n\n1. Ахмаджонов Али - 950 баллов\n2. Валиева Зебо - 920 баллов\n3. Каримов Бобур - 890 баллов\n\n<i>Скоро полный рейтинг будет добавлен...</i>",
            "en": "⭐ <b>Rating</b>\n\n🏆 <b>Top 10 participants:</b>\n\n1. Akhmadjonov Ali - 950 points\n2. Valieva Zebo - 920 points\n3. Karimov Bobur - 890 points\n\n<i>Full rating will be added soon...</i>"
        },
        "admin_help": {
            "uz": "👨‍💼 <b>Admin Yordami</b>\n\nSavollaringiz bo'lsa, admin bilan bog'laning:\n\n📱 Telegram: @admin_username\n📧 Email: admin@worldskills.uz\n📞 Telefon: +998 90 123 45 67\n\n<i>Tez orada javob beramiz!</i>",
            "ru": "👨‍💼 <b>Помощь админа</b>\n\nЕсли у вас есть вопросы, свяжитесь с админом:\n\n📱 Telegram: @admin_username\n📧 Email: admin@worldskills.uz\n📞 Телефон: +998 90 123 45 67\n\n<i>Мы скоро ответим!</i>",
            "en": "👨‍💼 <b>Admin Help</b>\n\nIf you have questions, contact admin:\n\n📱 Telegram: @admin_username\n📧 Email: admin@worldskills.uz\n📞 Phone: +998 90 123 45 67\n\n<i>We'll respond soon!</i>"
        },
        "change_profession": {
            "uz": "<b>Yangi kasbingizni tanlang:</b>",
            "ru": "<b>Выберите новую профессию:</b>",
            "en": "<b>Select your new profession:</b>"
        }
    }
    return translations.get(key, {}).get(lang, translations.get(key, {}).get("en", ""))

# ========== HANDLERS ==========

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """1-QADAM: Til tanlash"""
    await state.clear()
    await message.answer(
        t("welcome", "uz"),
        reply_markup=get_language_keyboard()
    )

@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery, state: FSMContext):
    """2-QADAM: Til tanlandi - ro'yxatdan o'tishga o'tish"""
    lang = callback.data.split("_")[1]
    
    # Tilni state'da saqlash
    await state.update_data(language=lang)
    
    await callback.message.answer(
        t("lang_selected", lang),
        reply_markup=get_profession_keyboard(lang)
    )
    
    # Ro'yxatdan o'tish state'iga o'tish
    await state.set_state(UserState.waiting_for_fullname)
    await callback.answer()

@router.message(UserState.waiting_for_fullname)
async def process_fullname(message: Message, state: FSMContext):
    """3-QADAM: Ism familiya qabul qilish"""
    user_data = await state.get_data()
    lang = user_data.get("language", "uz")
    fullname = message.text.strip()
    
    if len(fullname) < 3:
        await message.answer(t("invalid_name", lang))
        return
    
    await state.update_data(fullname=fullname)
    await state.set_state(UserState.waiting_for_phone)
    
    await message.answer(t("enter_phone", lang).format(name=fullname))

@router.message(UserState.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """4-QADAM: Telefon raqam qabul qilish"""
    user_data = await state.get_data()
    lang = user_data.get("language", "uz")
    phone = message.text.strip()
    
    if not phone.startswith("+") or len(phone) < 12:
        await message.answer(t("invalid_phone", lang))
        return
    
    await state.update_data(phone=phone)
    await state.set_state(UserState.waiting_for_profession)
    
    await message.answer(
        t("select_profession", lang).format(phone=phone),
        reply_markup=get_profession_keyboard(lang)
    )

@router.callback_query(UserState.waiting_for_profession)
async def process_profession(callback: CallbackQuery, state: FSMContext):
    """5-QADAM: Kasb tanlash - ro'yxatdan o'tish tugadi"""
    user_data = await state.get_data()
    lang = user_data.get("language", "uz")
    fullname = user_data.get("fullname")
    phone = user_data.get("phone")
    profession = callback.data.replace("prof_", "")
    
    await state.clear()
    
    await callback.message.answer(
        t("registration_complete", lang).format(name=fullname, prof=profession, phone=phone),
        reply_markup=get_main_menu_keyboard(lang)
    )
    await callback.answer()

# ========== AI MODE HANDLERS ==========

@router.message(F.text == "🤖 AI yordamchi" or F.text == "🤖 AI помощник" or F.text == "🤖 AI assistant")
async def enable_ai_mode(message: Message, state: FSMContext):
    """AI mode'ni yoqish"""
    user_data = await state.get_data()
    lang = user_data.get("language", "uz")
    
    await state.set_state(UserState.ai_mode)
    await message.answer(t("ai_welcome", lang))

@router.message(Command("start"))
async def exit_ai_mode(message: Message, state: FSMContext):
    """AI mode'dan chiqish"""
    user_data = await state.get_data()
    lang = user_data.get("language", "uz")
    
    await state.clear()
    await message.answer(
        t("welcome", lang),
        reply_markup=get_language_keyboard()
    )

# ========== ASOSIY MENYU TUGMALARI (faqat ro'yxatdan o'tganlar uchun) ==========

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
    user_data = await message.bot.get_user_profile_photos(message.from_user.id)
    # Bu yerda database'dan ma'lumot olish mumkin
    lang = "uz"  # Database'dan olish kerak
    await message.answer(t("stats", lang))

@router.message(F.text == "🏆 Mening musobaqam" or F.text == "🏆 Моё соревнование" or F.text == "🏆 My competition")
async def handle_competition(message: Message):
    lang = "uz"
    await message.answer(t("competition", lang))

@router.message(F.text == "⭐ Reyting" or F.text == "⭐ Рейтинг" or F.text == "⭐ Rating")
async def handle_rating(message: Message):
    lang = "uz"
    await message.answer(t("rating", lang))

@router.message(F.text == "👨‍💼 Admin yordami" or F.text == "👨‍💼 Помощь админа" or F.text == "👨‍💼 Admin help")
async def handle_admin(message: Message):
    lang = "uz"
    await message.answer(t("admin_help", lang))

@router.message(F.text == "🔄 Kasbni o'zgartirish" or F.text == "🔄 Сменить профессию" or F.text == "🔄 Change profession")
async def handle_change_profession(message: Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", "uz")
    await state.set_state(UserState.waiting_for_profession)
    await message.answer(t("change_profession", lang), reply_markup=get_profession_keyboard(lang))
