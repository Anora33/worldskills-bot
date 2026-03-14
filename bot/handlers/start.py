# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.keyboards.inline import get_start_keyboard, get_main_menu_keyboard, get_competition_keyboard, get_language_keyboard
from bot.states.states import RegistrationStates
from bot.database.database import async_session
from bot.database.queries import get_user_by_telegram_id, create_user, update_user_competition, add_points

router = Router()

TEXTS = {
    "uz": {
        "welcome": "?? WorldSkills Professional Botga xush kelibsiz!",
        "select_lang": "?? Iltimos, tilni tanlang:",
        "lang_changed": "? Til o'zgartirildi: {lang}",
        "main_menu": "?? Asosiy menyu",
        "start_btn": "?? Boshlash",
        "about_btn": "?? Bot haqida",
        "register_btn": "?? Ro'yxatdan o'tish",
        "schedule_btn": "?? Jadval",
        "competition_btn": "?? Yo'nalishim",
        "ai_btn": "?? AI Yordamchi",
        "rating_btn": "?? Reyting",
        "stats_btn": "?? Statistikam",
        "registration_started": "?? Ro'yxatdan o'tish\n\n1-qadam: To'liq ismingizni kiriting:\n\n<i>Masalan: Karimova Ozoda</i>",
        "name_saved": "? Ajoyib, {name}!\n\n2-qadam: O'z yo'nalishingizni tanlang:",
        "registration_complete": "?? Tabriklaymiz!\n\nSiz muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n?? Ism: {name}\n?? Yo'nalish: {competition}\n?? Ballar: 10\n\nEndi asosiy menyudan foydalanishingiz mumkin!",
        "already_registered": "? Siz allaqachon ro'yxatdan o'tgansiz!\n\n?? Ism: {name}\n?? Yo'nalish: {competition}\n?? Ballar: {points}",
        "about_bot": "?? Bot haqida\n\nWorldSkills Professional Bot - ishtirokchilar uchun maxsus yordamchi.\n\n?? Aloqa: @admin",
    },
    "ru": {
        "welcome": "?? Добро пожаловать в WorldSkills Professional Bot!",
        "select_lang": "?? Пожалуйста, выберите язык:",
        "lang_changed": "? Язык изменен: {lang}",
        "main_menu": "?? Главное меню",
        "start_btn": "?? Начать",
        "about_btn": "?? О боте",
        "register_btn": "?? Регистрация",
        "schedule_btn": "?? Расписание",
        "competition_btn": "?? Моя компетенция",
        "ai_btn": "?? AI помощник",
        "rating_btn": "?? Рейтинг",
        "stats_btn": "?? Моя статистика",
        "registration_started": "?? Регистрация\n\nШаг 1: Введите ваше полное имя:\n\n<i>Например: Каримова Озода</i>",
        "name_saved": "? Отлично, {name}!\n\nШаг 2: Выберите вашу компетенцию:",
        "registration_complete": "?? Поздравляем!\n\nВы успешно зарегистрированы!\n\n?? Имя: {name}\n?? Компетенция: {competition}\n?? Баллы: 10\n\nТеперь вы можете использовать главное меню!",
        "already_registered": "? Вы уже зарегистрированы!\n\n?? Имя: {name}\n?? Компетенция: {competition}\n?? Баллы: {points}",
        "about_bot": "?? О боте\n\nWorldSkills Professional Bot - специальный помощник для участников.\n\n?? Контакты: @admin",
    },
    "en": {
        "welcome": "?? Welcome to WorldSkills Professional Bot!",
        "select_lang": "?? Please select your language:",
        "lang_changed": "? Language changed: {lang}",
        "main_menu": "?? Main menu",
        "start_btn": "?? Start",
        "about_btn": "?? About bot",
        "register_btn": "?? Registration",
        "schedule_btn": "?? Schedule",
        "competition_btn": "?? My competition",
        "ai_btn": "?? AI assistant",
        "rating_btn": "?? Rating",
        "stats_btn": "?? My stats",
        "registration_started": "?? Registration\n\nStep 1: Enter your full name:\n\n<i>Example: Karimova Ozoda</i>",
        "name_saved": "? Great, {name}!\n\nStep 2: Choose your competition:",
        "registration_complete": "?? Congratulations!\n\nYou have successfully registered!\n\n?? Name: {name}\n?? Competition: {competition}\n?? Points: 10\n\nNow you can use the main menu!",
        "already_registered": "? You are already registered!\n\n?? Name: {name}\n?? Competition: {competition}\n?? Points: {points}",
        "about_bot": "?? About bot\n\nWorldSkills Professional Bot - special assistant for participants.\n\n?? Contact: @admin",
    }
}


def get_text(lang: str, key: str, **format_kwargs) -> str:
    try:
        text = TEXTS.get(lang, TEXTS["uz"]).get(key, key)
        if format_kwargs:
            text = text.format(**format_kwargs)
        return text
    except:
        return TEXTS["uz"].get(key, key)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    async with async_session() as db:
        user = await get_user_by_telegram_id(db, message.from_user.id)
    
    if user:
        lang = user.language or "uz"
        await message.answer(
            f"{get_text(lang, 'welcome')}\n\n{get_text(lang, 'main_menu')}",
            reply_markup=get_main_menu_keyboard(lang)
        )
    else:
        await message.answer(
            f"{get_text('uz', 'welcome')}\n\n{get_text('uz', 'select_lang')}",
            reply_markup=get_language_keyboard()
        )


@router.message(Command("lang"))
async def cmd_language(message: Message):
    await message.answer(
        "?? Tilni tanlang / Select language / Выберите язык:",
        reply_markup=get_language_keyboard()
    )


@router.callback_query(F.data.startswith("lang_"))
async def process_language_change(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.replace("lang_", "")
    
    async with async_session() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
        if user:
            user.language = lang
            await db.commit()
        else:
            await state.set_data({"temp_lang": lang})
    
    await callback.message.edit_text(
        get_text(lang, "lang_changed").format(lang=lang.upper())
    )
    await callback.answer()
    
    if user:
        await callback.message.answer(
            get_text(lang, "main_menu"),
            reply_markup=get_main_menu_keyboard(lang)
        )
    else:
        await callback.message.answer(
            f"{get_text(lang, 'welcome')}\n\n{get_text(lang, 'select_lang')}",
            reply_markup=get_start_keyboard(lang)
        )


@router.callback_query(F.data == "start_registration")
async def process_start_registration(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    lang = state_data.get("temp_lang", "uz")
    
    await state.set_state(RegistrationStates.full_name)
    await state.update_data(lang=lang)
    
    await callback.message.edit_text(
        get_text(lang, "registration_started"),
        reply_markup=None
    )
    await callback.answer()


@router.message(RegistrationStates.full_name)
async def process_full_name(message: Message, state: FSMContext):
    state_data = await state.get_data()
    lang = state_data.get("lang", "uz")
    
    full_name = message.text.strip()
    
    if len(full_name) < 3:
        await message.answer("? Iltimos, to'liq ismingizni kiriting (kamida 3 ta belgi)!")
        return
    
    await state.update_data(full_name=full_name)
    await state.set_state(RegistrationStates.competition)
    
    await message.answer(
        get_text(lang, "name_saved", name=full_name),
        reply_markup=get_competition_keyboard(lang)
    )


@router.callback_query(RegistrationStates.competition)
async def process_competition(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    lang = state_data.get("lang", "uz")
    full_name = state_data.get("full_name", "Unknown")
    
    competition_data = callback.data
    
    competition_names = {
        "comp_it_software": {"uz": "?? IT dasturiy ta'minot", "ru": "?? IT программное обеспечение", "en": "?? IT Software"},
        "comp_graphic_design": {"uz": "?? Grafik dizayn", "ru": "?? Графический дизайн", "en": "?? Graphic Design"},
        "comp_mechanics": {"uz": "?? Mexanika", "ru": "?? Механика", "en": "?? Mechanics"},
        "comp_culinary": {"uz": "????? Oshpazlik", "ru": "??? Кулинария", "en": "????? Culinary"},
        "comp_electronics": {"uz": "? Elektronika", "ru": "? Электроника", "en": "? Electronics"},
        "comp_construction": {"uz": "??? Qurilish", "ru": "??? Строительство", "en": "??? Construction"},
    }
    
    competition_name = competition_names.get(competition_data, {}).get(lang, competition_data)
    
    async with async_session() as db:
        user = await create_user(
            db=db,
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
            full_name=full_name,
            language=lang
        )
        await update_user_competition(db, callback.from_user.id, competition_name)
        await add_points(db, callback.from_user.id, 10)
    
    await state.clear()
    
    await callback.message.edit_text(
        get_text(lang, "registration_complete", name=full_name, competition=competition_name),
        reply_markup=get_main_menu_keyboard(lang)
    )
    await callback.answer("? Ro'yxatdan o'tdingiz!")


@router.callback_query(F.data == "about_bot")
async def process_about_bot(callback: CallbackQuery):
    async with async_session() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
    
    lang = user.language if user else "uz"
    await callback.message.edit_text(get_text(lang, "about_bot"))
    await callback.answer()


@router.callback_query(F.data == "register")
async def process_register_menu(callback: CallbackQuery):
    async with async_session() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
    
    lang = user.language if user else "uz"
    
    if user:
        await callback.message.answer(
            get_text(lang, "already_registered", 
                    name=user.full_name, 
                    competition=user.competition or "Tanlanmagan",
                    points=user.points),
            reply_markup=get_main_menu_keyboard(lang)
        )
    else:
        await callback.message.answer(
            "? Siz hali ro'yxatdan o'tmagansiz!",
            reply_markup=get_main_menu_keyboard(lang)
        )
    await callback.answer()


@router.callback_query(F.data == "schedule")
async def process_schedule(callback: CallbackQuery):
    async with async_session() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
    
    lang = user.language if user else "uz"
    await callback.message.answer(
        "?? Jadval\n\nMusobaqa jadvali tez orada qo'shiladi!",
        reply_markup=get_main_menu_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "my_competition")
async def process_my_competition(callback: CallbackQuery):
    async with async_session() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
    
    lang = user.language if user else "uz"
    
    if user and user.competition:
        await callback.message.answer(
            f"?? {get_text(lang, 'competition_btn')}\n\n{user.competition}\n\n?? Ballar: {user.points}",
            reply_markup=get_main_menu_keyboard(lang)
        )
    else:
        await callback.message.answer(
            "? Siz hali ro'yxatdan o'tmagansiz!",
            reply_markup=get_main_menu_keyboard(lang)
        )
    await callback.answer()


@router.callback_query(F.data == "rating")
async def process_rating(callback: CallbackQuery):
    async with async_session() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
    
    lang = user.language if user else "uz"
    await callback.message.answer(
        "?? Reyting\n\nTez orada qo'shiladi!",
        reply_markup=get_main_menu_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "stats")
async def process_stats(callback: CallbackQuery):
    async with async_session() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
    
    lang = user.language if user else "uz"
    
    if user:
        reg_date = user.registered_at.strftime("%d.%m.%Y %H:%M") if user.registered_at else "N/A"
        await callback.message.answer(
            f"?? {get_text(lang, 'stats_btn')}\n\n?? Ism: {user.full_name}\n?? Yo'nalish: {user.competition or 'Tanlanmagan'}\n?? Ballar: {user.points}\n?? Ro'yxatdan o'tgan: {reg_date}",
            reply_markup=get_main_menu_keyboard(lang)
        )
    else:
        await callback.message.answer(
            "? Siz hali ro'yxatdan o'tmagansiz!",
            reply_markup=get_main_menu_keyboard(lang)
        )
    await callback.answer()

