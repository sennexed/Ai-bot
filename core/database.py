import os
import asyncpg

pool = None

async def init_db():
    global pool
    pool = await asyncpg.create_pool(os.getenv("DATABASE_URL"))

    async with pool.acquire() as conn:

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS guild_settings (
            guild_id BIGINT PRIMARY KEY,
            log_channel BIGINT,
            ai_enabled BOOLEAN DEFAULT TRUE,
            ai_strictness INTEGER DEFAULT 3
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
            explanation TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)


async def ensure_guild(guild_id):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO guild_settings (guild_id)
        VALUES ($1)
        ON CONFLICT (guild_id) DO NOTHING;
        """, guild_id)


async def set_log_channel(guild_id, channel_id):
    await ensure_guild(guild_id)
    async with pool.acquire() as conn:
        await conn.execute("""
        UPDATE guild_settings
        SET log_channel=$1
        WHERE guild_id=$2;
        """, channel_id, guild_id)


async def get_log_channel(guild_id):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
        SELECT log_channel FROM guild_settings
        WHERE guild_id=$1;
        """, guild_id)
        return row["log_channel"] if row else None


async def get_guild_settings(guild_id):
    async with pool.acquire() as conn:
        return await conn.fetchrow("""
        SELECT * FROM guild_settings WHERE guild_id=$1;
        """, guild_id)


async def toggle_ai(guild_id):
    await ensure_guild(guild_id)
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
        UPDATE guild_settings
        SET ai_enabled = NOT ai_enabled
        WHERE guild_id=$1
        RETURNING ai_enabled;
        """, guild_id)
        return row["ai_enabled"]


async def set_strictness(guild_id, level):
    await ensure_guild(guild_id)
    async with pool.acquire() as conn:
        await conn.execute("""
        UPDATE guild_settings
        SET ai_strictness=$1
        WHERE guild_id=$2;
        """, level, guild_id)


async def add_infraction(guild_id, user_id, moderator_id, action, reason, severity, explanation):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO infractions
        (guild_id, user_id, moderator_id, action, reason, severity, explanation)
        VALUES ($1,$2,$3,$4,$5,$6,$7);
        """, guild_id, user_id, moderator_id, action, reason, severity, explanation)


async def count_user_infractions(guild_id, user_id):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
        SELECT COUNT(*) FROM infractions
        WHERE guild_id=$1 AND user_id=$2;
        """, guild_id, user_id)
        return row["count"]
