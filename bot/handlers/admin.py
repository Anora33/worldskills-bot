# -*- coding: utf-8 -*-
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message
from bot.database.database import async_session
from bot.database.queries import get_user_by_telegram_id
import os
from sqlalchemy import select, func
from bot.database.models import User

router = Router()


def is_admin(telegram_id: int) -> bool:
    """Adminligini tekshirish"""
    return telegram_id == int(os.environ.get('ADMIN_ID', 0))


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Admin panel - bosh menyu"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Siz admin emassiz!")
        return
    
    async with async_session() as db:
        count = await db.scalar(select(func.count(User.id)))
    
    await message.answer(
        f"🔐 <b>Admin Panel</b>\n\n"
        f"👥 Ro'yxatdan o'tgan foydalanuvchilar: <b>{count}</b>\n\n"
        f"📋 Buyruqlar:\n"
        f"• /users - Barcha foydalanuvchilar ro'yxati\n"
        f"• /user ID - Foydalanuvchi ma'lumotlari\n"
        f"• /works - Barcha yuborilgan ishlar\n"
        f"• /grade ID baho - Ishni baholash (1-5)\n"
        f"• /stats - Umumiy statistika\n"
        f"• /export - Foydalanuvchilarni faylga eksport qilish",
        parse_mode="HTML"
    )


@router.message(Command("works"))
async def cmd_all_works(message: Message):
    """Barcha yuborilgan ishlarni ko'rish"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Siz admin emassiz!")
        return
    
    await message.answer(
        "📸 <b>Barcha ishlar</b>\n\n"
        "1. Anor Karimova - Veb-sayt loyihasi\n"
        "   Status: Kutilmoqda ⏳\n\n"
        "2. Ivan Petrov - Mexanizm dizayni\n"
        "   Status: Baholandi ✅ (4/5)\n\n"
        "Baholash uchun:\n"
        "/grade 123456789 5\n"
        "(ID va baho 1-5 oralig'ida)",
        parse_mode="HTML"
    )


@router.message(Command("grade"))
async def cmd_grade_work(message: Message):
    """Ishni baholash"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Siz admin emassiz!")
        return
    
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        grade = int(parts[2])
        
        if grade < 1 or grade > 5:
            await message.answer("❌ Baho 1 dan 5 gacha bo'lishi kerak!")
            return
        
        await message.answer(
            f"✅ Foydalanuvchi ID {user_id} ning ishi {grade}/5 ga baholandi!\n\n"
            f"Foydalanuvchiga +{grade * 5} ball qo'shildi."
        )
        
    except (IndexError, ValueError):
        await message.answer(
            "❌ To'g'ri format: /grade ID baho\n\n"
            "Masalan: /grade 123456789 4"
        )


@router.message(Command("users"))
async def cmd_users(message: Message):
    """Barcha foydalanuvchilar ro'yxati"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Siz admin emassiz!")
        return
    
    async with async_session() as db:
        users = await db.execute(select(User).order_by(User.registered_at.desc()).limit(50))
        users = users.scalars().all()
    
    if not users:
        await message.answer("📭 Hali hech kim ro'yxatdan o'tmagan!")
        return
    
    result = "👥 <b>Foydalanuvchilar (so'ngi " + str(len(users)) + " ta):</b>\n\n"
    
    for i, user in enumerate(users, 1):
        lang_flag = {"uz": "🇺🇿", "ru": "🇷🇺", "en": "🇬🇧"}.get(user.language, "🌍")
        reg_date = user.registered_at.strftime("%d.%m %H:%M") if user.registered_at else "N/A"
        comp = user.competition if user.competition else "Tanlanmagan"
        
        result += (
            f"{i}. <code>{user.telegram_id}</code> - {user.full_name}\n"
            f"   {lang_flag} {user.language.upper()} | "
            f"🎯 {comp} | "
            f"🏆 {user.points} ball\n"
            f"   📅 {reg_date}\n\n"
        )
    
    for chunk in [result[i:i+4000] for i in range(0, len(result), 4000)]:
        await message.answer(chunk, parse_mode="HTML")


@router.message(Command("user"))
async def cmd_user_info(message: Message):
    """Ma'lum bir foydalanuvchi haqida ma'lumot"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Siz admin emassiz!")
        return
    
    try:
        telegram_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        await message.answer("❌ To'g'ri format: /user ID\n\nMasalan: /user 123456789")
        return
    
    async with async_session() as db:
        user = await get_user_by_telegram_id(db, telegram_id)
    
    if not user:
        await message.answer(f"❌ Foydalanuvchi topilmadi (ID: {telegram_id})")
        return
    
    lang_flag = {"uz": "🇺🇿", "ru": "🇷🇺", "en": "🇬🇧"}.get(user.language, "🌍")
    username = "@" + user.username if user.username else "Yo'q"
    comp = user.competition if user.competition else "Tanlanmagan"
    reg_date = user.registered_at.strftime("%d.%m.%Y %H:%M") if user.registered_at else "N/A"
    active = "Ha" if user.is_active else "Yo'q"
    
    await message.answer(
        f"👤 <b>Foydalanuvchi ma'lumotlari</b>\n\n"
        f"🆔 Telegram ID: <code>{user.telegram_id}</code>\n"
        f"👤 Ism: {user.full_name}\n"
        f"🔖 Username: {username}\n"
        f"🌍 Til: {lang_flag} {user.language.upper()}\n"
        f"🎯 Yo'nalish: {comp}\n"
        f"🏆 Ballar: {user.points}\n"
        f"✅ Aktiv: {active}\n"
        f"📅 Ro'yxatdan o'tgan: {reg_date}",
        parse_mode="HTML"
    )


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Umumiy statistika"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Siz admin emassiz!")
        return
    
    async with async_session() as db:
        total_users = await db.scalar(select(func.count(User.id)))
        total_points = await db.scalar(select(func.sum(User.points))) or 0
        by_lang = await db.execute(
            select(User.language, func.count(User.id)).group_by(User.language)
        )
        by_lang = dict(by_lang.all())
        by_competition = await db.execute(
            select(User.competition, func.count(User.id)).group_by(User.competition)
        )
        by_competition = dict(by_competition.all())
    
    avg_points = total_points // total_users if total_users else 0
    
    stats_text = (
        f"📊 <b>Umumiy statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total_users}</b>\n"
        f"🏆 Jami ballar: <b>{total_points}</b>\n"
        f"⭐ O'rtacha ball: <b>{avg_points}</b>\n\n"
        f"🌍 <b>Tillar bo'yicha:</b>\n"
    )
    
    for lang, count in by_lang.items():
        flag = {"uz": "🇺🇿", "ru": "🇷🇺", "en": "🇬🇧"}.get(lang, "🌍")
        stats_text += f"   {flag} {lang.upper()}: {count}\n"
    
    stats_text += f"\n🎯 <b>Yo'nalishlar bo'yicha:</b>\n"
    for comp, count in by_competition.items():
        comp_name = comp if comp else "Tanlanmagan"
        stats_text += f"   • {comp_name}: {count}\n"
    
    await message.answer(stats_text, parse_mode="HTML")


@router.message(Command("export"))
async def cmd_export(message: Message):
    """Foydalanuvchilarni CSV faylga eksport qilish"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Siz admin emassiz!")
        return
    
    async with async_session() as db:
        users = await db.execute(select(User).order_by(User.registered_at))
        users = users.scalars().all()
    
    csv_content = "Telegram ID,Username,Full Name,Language,Competition,Points,Registered At\n"
    for user in users:
        username = user.username if user.username else ""
        comp = user.competition if user.competition else ""
        reg_date = user.registered_at.strftime("%Y-%m-%d %H:%M:%S") if user.registered_at else ""
        csv_content += (
            f"{user.telegram_id},"
            f"{username},"
            f'"{user.full_name}",'
            f"{user.language},"
            f'"{comp}",'
            f"{user.points},"
            f"{reg_date}\n"
        )
    
    filename = f"users_export_{message.from_user.id}.csv"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(csv_content)
    
    await message.answer_document(
        types.FSInputFile(filename),
        caption=f"📄 <b>Eksport qilindi!</b>\n\n👥 {len(users)} ta foydalanuvchi",
        parse_mode="HTML"
    )
    
    import os
    os.remove(filename)

