# -*- coding: utf-8 -*-
import aiohttp
import logging
from bot.config import GROQ_API_KEY, GROQ_API_URL, AI_MODEL

logger = logging.getLogger(__name__)

class GroqAIService:
    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.api_url = GROQ_API_URL
        self.model = AI_MODEL
    
    async def ask(self, question: str, context: str = "") -> str:
        if not self.api_key or not self.api_key.startswith("gsk_"):
            return self._fallback_answer(question)
        
        try:
            system_prompt = f"""Siz WorldSkills Uzbekistan botining AI yordamchisisiz.
🏆 WorldSkills Shanghai 2026 haqida ma'lumot berasiz.
📋 64 ta kasb bo'yicha maslahat berishingiz mumkin.
🗣️ Faqat O'ZBEK tilida javob bering.
😊 Do'stona, qisqa va foydali javoblar bering.
{context}
Foydalanuvchi savoliga javob bering:"""

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": question}
                        ],
                        "max_tokens": 500,
                        "temperature": 0.7
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"].strip()
                    else:
                        logger.error(f"Groq API error: {response.status}")
                        return self._fallback_answer(question)
        except Exception as e:
            logger.error(f"GroqAIService error: {e}")
            return self._fallback_answer(question)
    
    def _fallback_answer(self, question: str) -> str:
        q = question.lower()
        if "salom" in q: return "Assalomu alaykum! 🤖 WorldSkills AI yordamchisi sizga xizmat qilishdan xursand!"
        if "rahmat" in q: return "Arzimaydi! 😊 Yana savollaringiz bo'lsa, bemalol so'rang!"
        if "worldskills" in q: return "🏆 <b>WorldSkills</b> - jahon kasb mahorati chempionati! 2026-yil Shanxayda 64 ta kasb bo'yicha musobaqa."
        if "kasb" in q: return "🎓 <b>64 ta kasb</b> mavjud: Dasturlash, Mexatronika, Oshpazlik, Dizayn. Mini App'da batafsil ko'ring!"
        if "ro'yxat" in q: return "📝 <b>Ro'yxatdan o'tish:</b> Mini App'ni oching → Ism+Telefon → Kasb tanlang → Tayyor!"
        if "pdf" in q: return "📄 <b>PDF yuklash:</b> Mini App → Statistika → Fayl yuklash (max 10 MB)."
        if "ball" in q: return "⭐ <b>Ballar:</b> 0-100. Ish sifati(40)+Innovatsiya(20)+Texnik(25)+Taqdimot(15)."
        if "aloqa" in q: return "📞 <b>Admin:</b> @worldskills_admin | +998 71 123 45 67"
        return "🤔 Savolingizni tushunmadim. WorldSkills, kasblar, PDF, ballar haqida so'rang."
