# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.types import Message
import os
import httpx

router = Router()

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
# ✅ Yangi model: llama3-70b-8192 (avvalgisining o'rniga)
GROQ_MODEL = "llama3-70b-8192"

@router.message(F.text == "🤖 AI assistant")
async def handle_ai_assistant(message: Message):
    await message.answer(
        "🤖 <b>AI Assistant</b>\n\n"
        "Salom! Men WorldSkills bo'yicha yordamchiman.\n\n"
        "Menga savol bering:\n"
        "• Musobaqa haqida\n"
        "• Topshiriqlar haqida\n"
        "• Texnik yordam\n\n"
        "<i>Savolingizni yozing...</i>"
    )

@router.message(F.regexp(r"^(?!/).+$"))
async def ai_chat(message: Message):
    """AI bilan suhbat"""
    if not GROQ_API_KEY:
        await message.answer("❌ GROQ_API_KEY sozlanmagan!")
        return
    
    try:
        await message.chat.action("typing")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": GROQ_MODEL,  # ✅ Yangi model
                    "messages": [
                        {
                            "role": "system", 
                            "content": "Siz WorldSkills professional yordamchisisiz. Foydalanuvchilarga musobaqa, topshiriqlar va texnik savollar bo'yicha yordam berasiz. Qisqa, aniq va foydali javob bering."
                        },
                        {
                            "role": "user", 
                            "content": message.text
                        }
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data['choices'][0]['message']['content']
                await message.answer(ai_response)
            else:
                error_msg = response.json().get('error', {}).get('message', 'Noma'lum xato')
                await message.answer(f"❌ AI xatosi: {error_msg}")
                
    except Exception as e:
        await message.answer(f"❌ Xato: {str(e)[:200]}")
