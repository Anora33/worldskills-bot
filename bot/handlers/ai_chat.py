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

@router.message(F.text == "🤖 AI yordamchi")
async def ai_start(message: Message, state: FSMContext):
    """AI ni ishga tushirish"""
    logger.info(f"AI started for user {message.from_user.id}")
    
    # Tilni aniqlash (default: uz)
    user_data = await state.get_data()
    lang = user_data.get("language", "uz")
    
    await state.set_state(AIState.active)
    await state.update_data(language=lang)
    
    texts = {
        "uz": "🤖 <b>AI Yordamchi</b>\n\nSalom! Men sizga yordam berishga tayyorman.\n\nMenga savol bering:\n- Musobaqa haqida\n- Topshiriqlar haqida\n- Texnik yordam\n\n<i>Savolingizni yozing, men javob beraman!</i>\n\n<i>Chiqish uchun /start bosing</i>",
        "ru": "🤖 <b>AI Помощник</b>\n\nПривет! Я готов помочь.\n\nЗадайте вопрос:\n- О соревновании\n- О заданиях\n- Техническая помощь\n\n<i>Напишите вопрос, я отвечу!</i>\n\n<i>Для выхода нажмите /start</i>",
        "en": "🤖 <b>AI Assistant</b>\n\nHello! I'm ready to help.\n\nAsk me anything:\n- About competition\n- About tasks\n- Technical support\n\n<i>Type your question, I'll answer!</i>\n\n<i>Type /start to exit</i>"
    }
    
    await message.answer(texts.get(lang, texts["uz"]))

@router.message(AIState.active)
async def ai_response(message: Message, state: FSMContext):
    """AI javobi - faqat AI mode'da ishlaydi"""
    logger.info(f"AI request from {message.from_user.id}: {message.text}")
    
    # GROQ_API_KEY ni tekshirish
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY not found in environment!")
        await message.answer("❌ API key topilmadi! Admin bilan bog'laning.")
        await state.clear()
        return
    
    # Tilni olish
    user_data = await state.get_data()
    lang = user_data.get("language", "uz")
    
    try:
        await message.chat.action("typing")
        logger.info("Sending request to GROQ API...")
        
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
                        {"role": "system", "content": "Siz WorldSkills professional yordamchisisiz. Foydalanuvchilarga musobaqa, topshiriqlar va texnik savollar bo'yicha yordam berasiz. Javoblaringiz qisqa (max 300 belgi), aniq va foydali bo'lsin."},
                        {"role": "user", "content": message.text}
                    ],
                    "max_tokens": 300,
                    "temperature": 0.7
                }
            )
            
            logger.info(f"GROQ API response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                answer = data["choices"][0]["message"]["content"]
                logger.info(f"AI answer: {answer[:100]}")
                await message.answer(answer)
            else:
                error_text = response.text[:200]
                logger.error(f"GROQ error {response.status_code}: {error_text}")
                await message.answer(f"❌ AI xatosi: {response.status_code}")
                
    except httpx.TimeoutException:
        logger.error("GROQ API timeout")
        await message.answer("⏰ AI javob bermadi. Qayta urinib ko'ring.")
    except Exception as e:
        logger.error(f"AI exception: {str(e)}")
        await message.answer(f"❌ Xato: {str(e)[:100]}")

@router.message(Command("start"))
async def ai_exit(message: Message, state: FSMContext):
    """AI mode'dan chiqish"""
    current_state = await state.get_state()
    if current_state == AIState.active:
        await state.clear()
        logger.info(f"AI exited for user {message.from_user.id}")
        await message.answer("✅ AI mode'dan chiqdingiz. Asosiy menyu:")
