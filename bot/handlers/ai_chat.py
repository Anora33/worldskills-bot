# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
import httpx

router = Router()

# State
class AIState(StatesGroup):
    waiting_for_message = State()

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

@router.message(F.text == "🤖 AI yordamchi")
async def ai_start(message: Message, state: FSMContext):
    """AI ni ishga tushirish"""
    await state.set_state(AIState.waiting_for_message)
    await message.answer(
        "🤖 <b>AI yordamchi</b>\n\n"
        "Savolingizni yozing, men javob beraman.\n\n"
        "<i>Chiqish uchun /start bosing</i>"
    )

@router.message(AIState.waiting_for_message)
async def ai_response(message: Message, state: FSMContext):
    """AI javobi"""
    if not GROQ_API_KEY:
        await message.answer("❌ API key topilmadi!")
        await state.clear()
        return
    
    try:
        await message.chat.action("typing")
        
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
                        {"role": "system", "content": "Siz WorldSkills yordamchisisiz. Qisqa va aniq javob bering."},
                        {"role": "user", "content": message.text}
                    ],
                    "max_tokens": 300
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data["choices"][0]["message"]["content"]
                await message.answer(answer)
            else:
                await message.answer(f"❌ Xato: {response.status_code}")
                
    except Exception as e:
        await message.answer(f"❌ Xato: {str(e)[:100]}")

@router.message(Command("start"))
async def ai_exit(message: Message, state: FSMContext):
    """AI dan chiqish"""
    await state.clear()
    await message.answer("✅ AI dan chiqdingiz")
