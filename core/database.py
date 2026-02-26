import os
import asyncpg

pool = None

async def init_db():
    global pool

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set.")

    pool = await asyncpg.create_pool(database_url, min_size=1, max_size=5)

    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS guild_settings (
            guild_id BIGINT PRIMARY KEY,
            log_channel BIGINT,
            ai_enabled BOOLEAN DEFAULT TRUE,
            ai_strictness INTEGER DEFAULT 1
        );
        """)

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            guild_id BIGINT,
            user_id BIGINT,
            reputation INTEGER DEFAULT 0,
            PRIMARY KEY (guild_id, user_id)
        );
        """)

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS infractions (
            id SERIAL PRIMARY KEY,
            guild_id BIGINT,
            user_id BIGINT,
            moderator_id BIGINT,
            action TEXT,
            reason TEXT,
            severity INTEGER,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

async def add_infraction(guild_id, user_id, moderator_id, action, reason, severity):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO infractions
        (guild_id, user_id, moderator_id, action, reason, severity)
        VALUES ($1,$2,$3,$4,$5,$6);
        """, guild_id, user_id, moderator_id, action, reason, severity)

async def get_user_reputation(guild_id, user_id):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
        SELECT reputation FROM users
        WHERE guild_id=$1 AND user_id=$2;
        """, guild_id, user_id)
        return row["reputation"] if row else 0

async def set_user_reputation(guild_id, user_id, value):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO users (guild_id, user_id, reputation)
        VALUES ($1,$2,$3)
        ON CONFLICT (guild_id, user_id)
        DO UPDATE SET reputation = EXCLUDED.reputation;
        """, guild_id, user_id, value)

async def get_user_infractions(guild_id, user_id):
    async with pool.acquire() as conn:
        return await conn.fetch("""
        SELECT * FROM infractions
        WHERE guild_id=$1 AND user_id=$2
        ORDER BY created_at DESC;
        """, guild_id, user_id)
