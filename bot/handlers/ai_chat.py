# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
import httpx
import logging

logger = logging.getLogger(__name__)
router = Router()

# State
class AIState(StatesGroup):
    active = State()

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

# AI tugmasi matnlari (barcha tillarda)
AI_BUTTONS = [
    "🤖 AI yordamchi",
    "🤖 AI помощник", 
    "🤖 AI assistant"
]

@router.message(F.text.in_(AI_BUTTONS))
async def ai_start(message: Message, state: FSMContext):
    """AI ni ishga tushirish - ENG BIRINCHI priority!"""
    logger.info(f"🤖 AI STARTED: user={message.from_user.id}, text={message.text}")
    
    user_data = await state.get_data()
    lang = user_data.get("language", "uz")
    
    await state.set_state(AIState.active)
    await state.update_data(language=lang)
    
    texts = {
        "uz": "🤖 <b>AI Yordamchi</b>\n\nSalom! Savolingizni yozing:",
        "ru": "🤖 <b>AI Помощник</b>\n\nПривет! Напишите вопрос:",
        "en": "🤖 <b>AI Assistant</b>\n\nHello! Type your question:"
    }
    
    await message.answer(texts.get(lang, texts["uz"]))

@router.message(AIState.active)
async def ai_response(message: Message, state: FSMContext):
    """AI javobi - faqat AI mode'da"""
    logger.info(f"💬 AI REQUEST: user={message.from_user.id}, text={message.text[:50]}")
    
    if not GROQ_API_KEY:
        logger.error("❌ GROQ_API_KEY NOT FOUND!")
        await message.answer("❌ API key yo'q!")
        await state.clear()
        return
    
    user_data = await state.get_data()
    lang = user_data.get("language", "uz")
    
    try:
        await message.chat.action("typing")
        logger.info("📡 Sending to GROQ API...")
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama3-70b-8192",
                    "messages": [
                        {"role": "system", "content": "Siz WorldSkills yordamchisisiz. Qisqa javob bering."},
                        {"role": "user", "content": message.text}
                    ],
                    "max_tokens": 300
                }
            )
            
            logger.info(f"📥 GROQ RESPONSE: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                answer = data["choices"][0]["message"]["content"]
                logger.info(f"✅ AI ANSWER: {answer[:100]}")
                await message.answer(answer)
            else:
                error = response.text[:200]
                logger.error(f"❌ GROQ ERROR {response.status_code}: {error}")
                await message.answer(f"❌ Xato: {response.status_code}")
                
    except Exception as e:
        logger.error(f"❌ EXCEPTION: {str(e)}")
        await message.answer(f"❌ Xato: {str(e)[:100]}")

@router.message(Command("start"))
async def ai_exit(message: Message, state: FSMContext):
    """AI dan chiqish"""
    current_state = await state.get_state()
    if current_state == AIState.active:
        logger.info(f"🚪 AI EXITED: user={message.from_user.id}")
        await state.clear()
        await message.answer("✅ AI dan chiqdingiz")
