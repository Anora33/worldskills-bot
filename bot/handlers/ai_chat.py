# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton
import logging, random

logger = logging.getLogger(__name__)
router = Router()

RESP = {"salom": ["Assalomu alaykum! 😊", "Salom!"], "rahmat": ["Arzimaydi!", "Marhamat!"], "xayr": ["Xayr! 👋"]}

def simple_ans(t):
    t = t.lower()
    for k, v in RESP.items():
        if k in t: return random.choice(v)
    return "Qiziq savol!"

@router.message(F.text == "🤖 AI yordamchi")
async def ai_start(msg: Message, state: FSMContext):
    await state.update_data(ai_active=True)
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="🔙 Chiqish"))
    await msg.answer("🤖 <b>AI Yordamchi</b>\n\nSavolingizni yozing:")

@router.message(F.text == "🔙 Chiqish")
async def ai_exit(msg: Message, state: FSMContext):
    await state.update_data(ai_active=False)
    await state.clear()
    kb = ReplyKeyboardBuilder()
    for b in ["📱 Mini App", "📊 Mening statistikam", "🏆 Mening musobaqam", "🤖 AI yordamchi", "⭐ Reyting", "👨‍💼 Admin yordami"]:
        kb.row(KeyboardButton(text=b))
    await msg.answer("✅ AI mode dan chiqildi", reply_markup=kb.as_markup(resize_keyboard=True))

@router.message()
async def ai_handler(msg: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get("ai_active"): return
    ans = simple_ans(msg.text)
    await msg.answer(f"🤖 AI: {ans}")
