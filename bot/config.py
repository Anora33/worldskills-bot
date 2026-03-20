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

# Profession ID mapping (callback_data uchun - 64 byte limit!)
PROFESSION_MAP = {
    "prof_001": "Industrial Mechanics | Sanoat mexanikasi",
    "prof_002": "Mechatronics | Mexatronika",
    "prof_003": "Mechanical Engineering CAD | Mexanik muhandislik CAD",
    "prof_004": "CNC Turning | CNC tokarlik ishlovi",
    "prof_005": "CNC Milling | CNC frezalash",
    "prof_006": "Welding | Payvandlash",
    "prof_007": "Electronics | Elektronika",
    "prof_008": "Industrial Control | Sanoat boshqaruvi",
    "prof_009": "Autonomous Mobile Robotics | Avtonom mobil robototexnika",
    "prof_010": "Industry 4.0 | Sanoat 4.0 texnologiyalari",
    "prof_011": "Chemical Laboratory Technology | Kimyo laboratoriya texnologiyasi",
    "prof_012": "Water Technology | Suv texnologiyasi",
    "prof_013": "Additive Manufacturing | 3D chop etish",
    "prof_014": "Industrial Design Technology | Sanoat dizayn texnologiyasi",
    "prof_015": "Optoelectronic Technology | Optoelektron texnologiya",
    "prof_016": "Renewable Energy | Qayta tiklanuvchi energiya",
    "prof_017": "Robot Systems Integration | Robot tizimlarini integratsiyalash",
    "prof_018": "ICT Network Infrastructure | AKT tarmoq infratuzilmasi",
    "prof_019": "Mobile Applications Development | Mobil ilovalar ishlab chiqish",
    "prof_020": "Software Applications Development | Dasturiy ta'minot ishlab chiqish",
    "prof_021": "Web Technologies | Veb texnologiyalar",
    "prof_022": "IT Network Systems Administration | Kompyuter tarmoqlarini boshqarish",
    "prof_023": "Cloud Computing | Bulutli hisoblash",
    "prof_024": "Cyber Security | Kiberxavfsizlik",
    "prof_025": "Software Testing | Dasturiy ta'minotni sinash",
    "prof_026": "Wall and Floor Tiling | Devor va pol plitkalash",
    "prof_027": "Plumbing and Heating | Santexnika va isitish tizimlari",
    "prof_028": "Electrical Installations | Elektr o'rnatish ishlari",
    "prof_029": "Bricklaying | G'isht terish",
    "prof_030": "Plastering and Drywall Systems | Suvoq va gipsokarton tizimlari",
    "prof_031": "Painting and Decorating | Bo'yash va bezatish",
    "prof_032": "Cabinetmaking | Shkaf yasash duradgorlik",
    "prof_033": "Joinery | Duradgorlik yig'ish ishlari",
    "prof_034": "Carpentry | Duradgorlik yog'och ishlari",
    "prof_035": "Landscape Gardening | Landshaft bog'dorchiligi",
    "prof_036": "Refrigeration and Air Conditioning | Sovutish va konditsioner tizimlari",
    "prof_037": "Concrete Construction Work | Beton qurilish ishlari",
    "prof_038": "Digital Construction | Raqamli qurilish",
    "prof_039": "Intelligent Security Technology | Aqlli xavfsizlik texnologiyalari",
    "prof_040": "Autobody Repair | Avtomobil kuzovini ta'mirlash",
    "prof_041": "Aircraft Maintenance | Samolyotlarga texnik xizmat",
    "prof_042": "Automobile Technology | Avtomobil texnologiyasi",
    "prof_043": "Car Painting | Avtomobil bo'yash",
    "prof_044": "Heavy Vehicle Technology | Og'ir transport texnologiyasi",
    "prof_045": "Logistics and Freight Forwarding | Logistika va yuk tashish",
    "prof_046": "Rail Vehicle Technology | Temiryo'l transporti texnologiyasi",
    "prof_047": "Unmanned Aerial Systems | Uchuvchisiz uchish apparatlari",
    "prof_048": "Jewellery | Zargarlik",
    "prof_049": "Floristry | Gulchilik san'ati",
    "prof_050": "Fashion Technology | Moda texnologiyasi",
    "prof_051": "Graphic Design Technology | Grafik dizayn texnologiyasi",
    "prof_052": "Visual Merchandising | Vizual savdo bezagi",
    "prof_053": "3D Digital Game Art | 3D raqamli o'yin san'ati",
    "prof_054": "Digital Interactive Media Design | Raqamli interaktiv media dizayni",
    "prof_055": "Hairdressing | Sartaroshlik",
    "prof_056": "Beauty Therapy | Go'zallik terapiyasi",
    "prof_057": "Pâtisserie and Confectionery | Pishiriqlar va shirinliklar",
    "prof_058": "Cooking | Oshpazlik",
    "prof_059": "Restaurant Service | Restoran xizmati",
    "prof_060": "Health and Social Care | Sog'liqni saqlash va ijtimoiy g'amxo'rlik",
    "prof_061": "Bakery | Nonvoychilik",
    "prof_062": "Hotel Reception | Mehmonxona qabulxonasi",
    "prof_063": "Dental Prosthetics | Tish protezlash",
    "prof_064": "Retail Sales | Chakana savdo"
}

# Category mapping (callback_data uchun)
CATEGORY_MAP = {
    "cat_001": "🏭 Ishlab chiqarish va Muhandislik",
    "cat_002": "💻 Axborot va Kommunikatsiya",
    "cat_003": "🏗️ Qurilish va Bino Texnologiyalari",
    "cat_004": "🚚 Transport va Logistika",
    "cat_005": "🎨 Ijodiy San'at va Moda",
    "cat_006": "👥 Ijtimoiy va Shaxsiy Xizmatlar"
}

# Profession IDs by category
PROFESSIONS_BY_CATEGORY = {
    "cat_001": ["prof_001","prof_002","prof_003","prof_004","prof_005","prof_006","prof_007","prof_008","prof_009","prof_010","prof_011","prof_012","prof_013","prof_014","prof_015","prof_016","prof_017"],
    "cat_002": ["prof_018","prof_019","prof_020","prof_021","prof_022","prof_023","prof_024","prof_025"],
    "cat_003": ["prof_026","prof_027","prof_028","prof_029","prof_030","prof_031","prof_032","prof_033","prof_034","prof_035","prof_036","prof_037","prof_038","prof_039"],
    "cat_004": ["prof_040","prof_041","prof_042","prof_043","prof_044","prof_045","prof_046","prof_047"],
    "cat_005": ["prof_048","prof_049","prof_050","prof_051","prof_052","prof_053","prof_054"],
    "cat_006": ["prof_055","prof_056","prof_057","prof_058","prof_059","prof_060","prof_061","prof_062","prof_063","prof_064"]
}
