from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp, bot
from utils.db_api import database as db
import logging


# Ro'yxatdan o'tganlikni tekshirish
async def check_user_registered(user_id):
    conn = await db.get_connection()
    user = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
    await conn.close()
    return user is not None


# Asosiy menyu (siz korsatgan menyu)
def get_main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("👤 Mening profilim", callback_data="my_profile"),
        InlineKeyboardButton("📋 Mening ishlarim", callback_data="my_works"),
        InlineKeyboardButton("ℹ️ WorldSkills haqida", callback_data="about"),
        InlineKeyboardButton("📊 Statistika", callback_data="statistics"),
        InlineKeyboardButton("❌ Yopish", callback_data="close_menu")
    ]
    keyboard.add(*buttons)
    return keyboard


# Ro'yxatdan o'tish tugmasi
def get_register_button():
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton("📝 Ro'yxatdan o'tish", callback_data="register")
    keyboard.add(button)
    return keyboard


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # Foydalanuvchi ro'yxatdan o'tganmi tekshirish
    is_registered = await check_user_registered(user_id)

    if is_registered:
        # Ro'yxatdan o'tgan bo'lsa - asosiy menyuni ko'rsat
        await message.answer(
            f"👋 Xush kelibsiz, {user_name}!\n\n"
            f"Quyidagi bo'limlardan birini tanlang:",
            reply_markup=get_main_menu()
        )
    else:
        # Ro'yxatdan o'tmagan bo'lsa - register tugmasini ko'rsat
        await message.answer(
            f"👋 Assalomu alaykum, {user_name}!\n\n"
            f"Botdan foydalanish uchun avval ro'yxatdan o'ting:",
            reply_markup=get_register_button()
        )


@dp.callback_query_handler(text="register")
async def process_register(callback: types.CallbackQuery):
    await callback.answer()

    user_id = callback.from_user.id
    user_name = callback.from_user.first_name

    # Ma'lumotlar bazasiga saqlash
    conn = await db.get_connection()
    await conn.execute(
        "INSERT INTO users (user_id, name, registered_at) VALUES ($1, $2, NOW())",
        user_id, user_name
    )
    await conn.close()

    # Ro'yxatdan o'tganlik haqida xabar va asosiy menyu
    await callback.message.edit_text(
        f"✅ Tabriklaymiz!\n"
        f"Siz muvaffaqiyatli ro'yxatdan o'tdingiz.\n\n"
        f"Endi quyidagi bo'limlardan foydalanishingiz mumkin:",
        reply_markup=get_main_menu()
    )


@dp.callback_query_handler(text="my_profile")
async def show_profile(callback: types.CallbackQuery):
    await callback.answer()

    user_id = callback.from_user.id
    conn = await db.get_connection()
    user = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
    await conn.close()

    if user:
        text = f"""
👤 <b>MENING PROFILIM</b>

🆔 ID: <code>{user['user_id']}</code>
📝 Ism: {user.get('first_name', 'Noma\'lum')}
📞 Telefon: {user.get('phone', 'Noma\'lum')}
📚 Yo'nalish: {user.get('direction', 'Noma\'lum')}
⭐️ Ball: {user.get('ball', 0)}
        """
    else:
        text = "❌ Profil ma'lumotlari topilmadi"

    await callback.message.answer(text, parse_mode="HTML")


@dp.callback_query_handler(text="my_works")
async def show_works(callback: types.CallbackQuery):
    await callback.answer()

    text = """
📋 <b>MENING ISHLARIM</b>

1. Web sahifa - 85 ball ✅
2. Telegram bot - 92 ball ✅
3. Database loyiha - 78 ball ✅

📊 Jami: 3 ta ish
🏆 O'rtacha ball: 85
    """

    await callback.message.answer(text, parse_mode="HTML")


@dp.callback_query_handler(text="about")
async def show_about(callback: types.CallbackQuery):
    await callback.answer()

    text = """
ℹ️ <b>WORLDSKILLS HAQIDA</b>

WorldSkills — professional mahorat bo'yicha jahon chempionati.

🌍 80+ davlat
🏆 60+ yo'nalish
📅 Har 2 yilda o'tkaziladi

🇺🇿 O'zbekiston 2018 yildan beri ishtirok etadi.
    """

    await callback.message.answer(text, parse_mode="HTML")


@dp.callback_query_handler(text="statistics")
async def show_statistics(callback: types.CallbackQuery):
    await callback.answer()

    conn = await db.get_connection()
    total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
    await conn.close()

    text = f"""
📊 <b>STATISTIKA</b>

👥 Ro'yxatdan o'tganlar: {total_users} ta
📈 Faol foydalanuvchilar: 15 ta
🏆 Eng yaxshi yo'nalish: Web texnologiyalar
    """

    await callback.message.answer(text, parse_mode="HTML")


@dp.callback_query_handler(text="close_menu")
async def close_menu(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("❌ Menyu yopildi. Qayta boshlash uchun /start bosing.")