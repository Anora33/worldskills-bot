# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Mini App", callback_data="mini_app"))
    builder.row(InlineKeyboardButton(text="Statistika", callback_data="stats"))
    builder.row(InlineKeyboardButton(text="Yordam", callback_data="help"))
    
    await message.answer(
        "WorldSkills Professional Bot\n\n"
        "Xush kelibsiz!\n\n"
        "Mini App orqali ro'yxatdan o'ting\n"
        "Statistika va natijalaringizni ko'ring\n"
        "Yordam uchun /help\n\n"
        "Mini App tugmasini bosing!",
        reply_markup=builder.as_markup()
    )
