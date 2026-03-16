# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.types import Message, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.config import WEBAPP_URL
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text == "📱 Mini App")
async def mini_app(msg: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Ochish", web_app=WebAppInfo(url=WEBAPP_URL))
    await msg.answer("📱 <b>Mini App</b>", reply_markup=kb.as_markup(), parse_mode="HTML")
