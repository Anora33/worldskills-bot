from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.database.models import User


async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int) -> User | None:
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, telegram_id: int, username: str, full_name: str, language: str = "uz") -> User:
    user = User(
        telegram_id=telegram_id,
        username=username,
        full_name=full_name,
        language=language
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_competition(db: AsyncSession, telegram_id: int, competition: str) -> bool:
    user = await get_user_by_telegram_id(db, telegram_id)
    if user:
        user.competition = competition
        await db.commit()
        return True
    return False


async def add_points(db: AsyncSession, telegram_id: int, points: int) -> bool:
    user = await get_user_by_telegram_id(db, telegram_id)
    if user:
        user.points += points
        await db.commit()
        return True
    return False
