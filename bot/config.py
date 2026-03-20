import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# Web App
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://worldskills-bot.onrender.com").strip()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "worldskills.db").strip()

# ✅ GROQ AI - Faqat environment variable'dan o'qiladi!
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()  # ❌ Hech qachon bu yerga kalit yozmang!
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
AI_MODEL = "llama3-70b-8192"

# WorldSkills Info
WORLDSKILLS_INFO = {
    "name": "WorldSkills Shanghai 2026",
    "edition": "48-chi Jahon Kasb Chempionati",
    "frequency": "Har 2 yilda bir marta",
    "description": "Yoshlarning kasbiy mahoratini rivojlantirish va namoyish etish uchun xalqaro musobaqa.",
    "significance": "Dunyo bo'ylab 80+ mamlakat ishtirok etadigan eng yirik kasb chempionati.",
    "organizers": ["WorldSkills International", "Shanghai Municipal Government"]
}

# Kategoriya va Kasblar
CATEGORY_MAP = {
    "cat_001": "🏭 Ishlab chiqarish va Muhandislik",
    "cat_002": "💻 Axborot va Kommunikatsiya",
    "cat_003": "🏗️ Qurilish va Bino Texnologiyalari",
    "cat_004": "🚚 Transport va Logistika",
    "cat_005": "🎨 Ijodiy San'at va Moda",
    "cat_006": "👥 Ijtimoiy va Shaxsiy Xizmatlar"
}

PROFESSIONS_BY_CATEGORY = {
    "cat_001": [f"prof_001_{i}" for i in range(1, 18)],
    "cat_002": [f"prof_002_{i}" for i in range(1, 9)],
    "cat_003": [f"prof_003_{i}" for i in range(1, 15)],
    "cat_004": [f"prof_004_{i}" for i in range(1, 9)],
    "cat_005": [f"prof_005_{i}" for i in range(1, 8)],
    "cat_006": [f"prof_006_{i}" for i in range(1, 11)]
}

PROFESSION_MAP = {
    # cat_001: Ishlab chiqarish (17 ta)
    "prof_001_1": "Industrial Mechanics | Sanoat mexanikasi",
    "prof_001_2": "Mechatronics | Mexatronika",
    "prof_001_3": "Mechanical Engineering CAD | Mexanik muhandislik CAD",
    "prof_001_4": "CNC Turning | CNC tokarlik ishlovi",
    "prof_001_5": "CNC Milling | CNC frezalash",
    "prof_001_6": "Welding | Payvandlash",
    "prof_001_7": "Electronics | Elektronika",
    "prof_001_8": "Industrial Control | Sanoat boshqaruvi",
    "prof_001_9": "Autonomous Mobile Robotics | Avtonom mobil robototexnika",
    "prof_001_10": "Industry 4.0 | Sanoat 4.0",
    "prof_001_11": "Chemical Laboratory Technology | Kimyo laboratoriya",
    "prof_001_12": "Water Technology | Suv texnologiyasi",
    "prof_001_13": "Additive Manufacturing | 3D chop etish",
    "prof_001_14": "Industrial Design Technology | Sanoat dizayni",
    "prof_001_15": "Optoelectronic Technology | Optoelektronika",
    "prof_001_16": "Renewable Energy | Qayta tiklanuvchi energiya",
    "prof_001_17": "Robot Systems Integration | Robot tizimlari",
    
    # cat_002: IT (8 ta)
    "prof_002_1": "ICT Network Infrastructure | Tarmoq infratuzilmasi",
    "prof_002_2": "Mobile Applications | Mobil ilovalar",
    "prof_002_3": "Software Development | Dasturiy ta'minot",
    "prof_002_4": "Web Technologies | Veb texnologiyalar",
    "prof_002_5": "IT Network Administration | Tarmoq boshqaruvi",
    "prof_002_6": "Cloud Computing | Bulutli hisoblash",
    "prof_002_7": "Cyber Security | Kiberxavfsizlik",
    "prof_002_8": "Software Testing | Dasturiy sinov",
    
    # cat_003: Qurilish (14 ta)
    "prof_003_1": "Wall and Floor Tiling | Plitkalash",
    "prof_003_2": "Plumbing and Heating | Santexnika",
    "prof_003_3": "Electrical Installations | Elektr o'rnatish",
    "prof_003_4": "Bricklaying | G'isht terish",
    "prof_003_5": "Plastering | Suvoq",
    "prof_003_6": "Painting | Bo'yash",
    "prof_003_7": "Cabinetmaking | Duradgorlik",
    "prof_003_8": "Joinery | Yig'ish ishlari",
    "prof_003_9": "Carpentry | Yog'och ishlari",
    "prof_003_10": "Landscape Gardening | Landshaft",
    "prof_003_11": "Refrigeration | Sovutish",
    "prof_003_12": "Concrete Work | Beton ishlari",
    "prof_003_13": "Digital Construction | Raqamli qurilish",
    "prof_003_14": "Security Technology | Xavfsizlik",
    
    # cat_004: Transport (8 ta)
    "prof_004_1": "Autobody Repair | Kuzov ta'mirlash",
    "prof_004_2": "Aircraft Maintenance | Samolyot xizmati",
    "prof_004_3": "Automobile Technology | Avtomobil",
    "prof_004_4": "Car Painting | Avtomobil bo'yash",
    "prof_004_5": "Heavy Vehicle | Og'ir transport",
    "prof_004_6": "Logistics | Logistika",
    "prof_004_7": "Rail Vehicle | Temiryo'l",
    "prof_004_8": "UAV Systems | Uchuvchisiz apparatlar",
    
    # cat_005: Ijodiy (7 ta)
    "prof_005_1": "Jewellery | Zargarlik",
    "prof_005_2": "Floristry | Gulchilik",
    "prof_005_3": "Fashion Technology | Moda",
    "prof_005_4": "Graphic Design | Grafik dizayn",
    "prof_005_5": "Visual Merchandising | Vizual savdo",
    "prof_005_6": "3D Game Art | 3D o'yin san'ati",
    "prof_005_7": "Media Design | Media dizayn",
    
    # cat_006: Xizmatlar (10 ta)
    "prof_006_1": "Hairdressing | Sartaroshlik",
    "prof_006_2": "Beauty Therapy | Go'zallik",
    "prof_006_3": "Pâtisserie | Qandolatchilik",
    "prof_006_4": "Cooking | Oshpazlik",
    "prof_006_5": "Restaurant Service | Restoran",
    "prof_006_6": "Health Care | Sog'liqni saqlash",
    "prof_006_7": "Bakery | Nonvoychilik",
    "prof_006_8": "Hotel Reception | Mehmonxona",
    "prof_006_9": "Dental Prosthetics | Tish protezi",
    "prof_006_10": "Retail Sales | Savdo"
}
