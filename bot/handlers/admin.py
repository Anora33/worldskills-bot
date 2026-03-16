# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.config import ADMIN_ID
from bot.database.db import get_all_users, get_user, update_user_status, add_log
import logging

logger = logging.getLogger(__name__)
router = Router()

class AdminState(StatesGroup):
    waiting_for_score = State()

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Faqat admin uchun!")
        return
    kb = InlineKeyboardBuilder()
    kb.button(text="📋 Barcha foydalanuvchilar", callback_data="admin_list")
    kb.button(text="📊 Statistika", callback_data="admin_stats")
    kb.adjust(1)
    await message.answer("👨‍💼 <b>Admin Panel</b>\n\nBo'limni tanlang:", reply_markup=kb.as_markup(), parse_mode="HTML")

@router.callback_query(F.data == "admin_list")
async def admin_list(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID: await cb.answer("❌", show_alert=True); return
    users = get_all_users()
    kb = InlineKeyboardBuilder()
    for u in users[:10]:
        kb.button(text=f"✅ {u.get('fullname','?')} ({u.get('profession','?')})", callback_data=f"admin_view_{u.get('telegram_id')}")
    kb.adjust(1)
    kb.button(text="🔙 Orqaga", callback_data="admin_back")
    await cb.message.edit_text(f"📋 Foydalanuvchilar ({len(users)} ta)", reply_markup=kb.as_markup())
    await cb.answer()

@router.callback_query(F.data.startswith("admin_view_"))
async def admin_view(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID: await cb.answer("❌", show_alert=True); return
    tid = int(cb.data.replace("admin_view_",""))
    u = get_user(tid)
    if not u: await cb.answer("❌ Topilmadi", show_alert=True); return
    kb = InlineKeyboardBuilder()
    kb.button(text="⭐ Baho qo'yish", callback_data=f"admin_score_{tid}")
    kb.button(text="🔙 Orqaga", callback_data="admin_list")
    kb.adjust(1)
    await cb.message.edit_text(f"👤 {u.get('fullname')}\n📱 {u.get('phone')}\n🎓 {u.get('profession')}\n⭐ Ball: {u.get('admin_score',0)}/100", reply_markup=kb.as_markup())
    await cb.answer()

@router.callback_query(F.data.startswith("admin_score_"))
async def admin_score(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID: await cb.answer("❌", show_alert=True); return
    await state.update_data(score_tid=int(cb.data.replace("admin_score_","")))
    await state.set_state(AdminState.waiting_for_score)
    await cb.message.answer("⭐ Baho kiriting (0-100):")
    await cb.answer()

@router.message(AdminState.waiting_for_score)
async def proc_score(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID: return
    try:
        sc = int(msg.text)
        if sc<0 or sc>100: await msg.answer("❌ 0-100 oralig'ida!"); return
        d = await state.get_data()
        tid = d.get("score_tid")
        update_user_status(tid, "approved", sc)
        add_log(tid, ADMIN_ID, "score", f"Ball: {sc}")
        try: await msg.bot.send_message(tid, f"⭐ Bahongiz: {sc}/100")
        except: pass
        await msg.answer(f"✅ Baho qo'yildi: {sc}/100")
        await state.clear()
    except: await msg.answer("❌ Raqam kiriting!")

@router.callback_query(F.data == "admin_back")
async def admin_back(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID: await cb.answer("❌", show_alert=True); return
    kb = InlineKeyboardBuilder()
    kb.button(text="📋 Barcha foydalanuvchilar", callback_data="admin_list")
    kb.button(text="📊 Statistika", callback_data="admin_stats")
    kb.adjust(1)
    await cb.message.edit_text("👨‍💼 <b>Admin Panel</b>\n\nBo'limni tanlang:", reply_markup=kb.as_markup(), parse_mode="HTML")
    await cb.answer()

@router.callback_query(F.data == "admin_stats")
async def admin_stats(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID: await cb.answer("❌", show_alert=True); return
    users = get_all_users()
    await cb.message.edit_text(f"📊 Statistika\n\n👥 Jami: {len(users)}", reply_markup=InlineKeyboardBuilder().button(text="🔙 Orqaga", callback_data="admin_back").as_markup())
    await cb.answer()
