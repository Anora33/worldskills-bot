import asyncpg
from data import config

class Database:
    def __init__(self):
        self.pool = None

    async def create_pool(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            database=config.DB_NAME,
            host=config.DB_HOST
        )

    async def get_connection(self):
        if not self.pool:
            await self.create_pool()
        return await self.pool.acquire()

    async def create_tables(self):
        conn = await self.get_connection()
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                phone VARCHAR(20),
                direction VARCHAR(100),
                ball INTEGER DEFAULT 0,
                registered_at TIMESTAMP DEFAULT NOW()
            )
        """)
        await conn.close()

database = Database()