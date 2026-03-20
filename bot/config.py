# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://worldskills-bot.onrender.com")
DATABASE_URL = os.getenv("DATABASE_URL", "worldskills.db")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# WorldSkills Shanghai 2026 Info
WORLDSKILLS_INFO = {
    "name": "WorldSkills Shanghai 2026",
    "edition": "48-chi Jahon Kasb Chempionati",
    "frequency": "Har ikki yilda bir marta",
    "organizers": [
        "Xitoy Xalq Respublikasi Inson resurslari va ijtimoiy xavfsizlik vazirligi",
        "Shanxay shahar xalq hukumati"
    ],
    "description": "WorldSkills Competition dunyodagi eng yirik texnik va kasblar chempionati hisoblanadi. Ushbu chempionat kasbiy mahoratning oltin standartini ifodalaydi.",
    "significance": "Ishtirokchi mamlakat yoki hududning yutuqlari uning iqtisodiy va texnologik salohiyati, shuningdek kasbiy rivojlanish darajasini aks ettiradi."
}

# 64 WorldSkills Professions by Category
PROFESSIONS = {
    "🏭 Ishlab chiqarish va Muhandislik": [
        "Industrial Mechanics | Sanoat mexanikasi",
        "Mechatronics | Mexatronika",
        "Mechanical Engineering CAD | Mexanik muhandislik CAD",
        "CNC Turning | CNC tokarlik ishlovi",
        "CNC Milling | CNC frezalash",
        "Welding | Payvandlash",
        "Electronics | Elektronika",
        "Industrial Control | Sanoat boshqaruvi",
        "Autonomous Mobile Robotics | Avtonom mobil robototexnika",
        "Industry 4.0 | Sanoat 4.0 texnologiyalari",
        "Chemical Laboratory Technology | Kimyo laboratoriya texnologiyasi",
        "Water Technology | Suv texnologiyasi",
        "Additive Manufacturing | 3D chop etish",
        "Industrial Design Technology | Sanoat dizayn texnologiyasi",
        "Optoelectronic Technology | Optoelektron texnologiya",
        "Renewable Energy | Qayta tiklanuvchi energiya",
        "Robot Systems Integration | Robot tizimlarini integratsiyalash"
    ],
    "💻 Axborot va Kommunikatsiya": [
        "ICT Network Infrastructure | AKT tarmoq infratuzilmasi",
        "Mobile Applications Development | Mobil ilovalar ishlab chiqish",
        "Software Applications Development | Dasturiy ta'minot ishlab chiqish",
        "Web Technologies | Veb texnologiyalar",
        "IT Network Systems Administration | Kompyuter tarmoqlarini boshqarish",
        "Cloud Computing | Bulutli hisoblash",
        "Cyber Security | Kiberxavfsizlik",
        "Software Testing | Dasturiy ta'minotni sinash"
    ],
    "🏗️ Qurilish va Bino Texnologiyalari": [
        "Wall and Floor Tiling | Devor va pol plitkalash",
        "Plumbing and Heating | Santexnika va isitish tizimlari",
        "Electrical Installations | Elektr o'rnatish ishlari",
        "Bricklaying | G'isht terish",
        "Plastering and Drywall Systems | Suvoq va gipsokarton tizimlari",
        "Painting and Decorating | Bo'yash va bezatish",
        "Cabinetmaking | Shkaf yasash duradgorlik",
        "Joinery | Duradgorlik yig'ish ishlari",
        "Carpentry | Duradgorlik yog'och ishlari",
        "Landscape Gardening | Landshaft bog'dorchiligi",
        "Refrigeration and Air Conditioning | Sovutish va konditsioner tizimlari",
        "Concrete Construction Work | Beton qurilish ishlari",
        "Digital Construction | Raqamli qurilish",
        "Intelligent Security Technology | Aqlli xavfsizlik texnologiyalari"
    ],
    "🚚 Transport va Logistika": [
        "Autobody Repair | Avtomobil kuzovini ta'mirlash",
        "Aircraft Maintenance | Samolyotlarga texnik xizmat",
        "Automobile Technology | Avtomobil texnologiyasi",
        "Car Painting | Avtomobil bo'yash",
        "Heavy Vehicle Technology | Og'ir transport texnologiyasi",
        "Logistics and Freight Forwarding | Logistika va yuk tashish",
        "Rail Vehicle Technology | Temiryo'l transporti texnologiyasi",
        "Unmanned Aerial Systems | Uchuvchisiz uchish apparatlari"
    ],
    "🎨 Ijodiy San'at va Moda": [
        "Jewellery | Zargarlik",
        "Floristry | Gulchilik san'ati",
        "Fashion Technology | Moda texnologiyasi",
        "Graphic Design Technology | Grafik dizayn texnologiyasi",
        "Visual Merchandising | Vizual savdo bezagi",
        "3D Digital Game Art | 3D raqamli o'yin san'ati",
        "Digital Interactive Media Design | Raqamli interaktiv media dizayni"
    ],
    "👥 Ijtimoiy va Shaxsiy Xizmatlar": [
        "Hairdressing | Sartaroshlik",
        "Beauty Therapy | Go'zallik terapiyasi",
        "Pâtisserie and Confectionery | Pishiriqlar va shirinliklar",
        "Cooking | Oshpazlik",
        "Restaurant Service | Restoran xizmati",
        "Health and Social Care | Sog'liqni saqlash va ijtimoiy g'amxo'rlik",
        "Bakery | Nonvoychilik",
        "Hotel Reception | Mehmonxona qabulxonasi",
        "Dental Prosthetics | Tish protezlash",
        "Retail Sales | Chakana savdo"
    ]
}

# Flatten professions for easy selection
ALL_PROFESSIONS = [p for category in PROFESSIONS.values() for p in category]
