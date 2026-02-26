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
            ai_strictness INTEGER DEFAULT 1,
            raid_mode BOOLEAN DEFAULT FALSE,
            lockdown BOOLEAN DEFAULT FALSE
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
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

# ---------------- SETTINGS ----------------

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

async def toggle_raid(guild_id):
    await ensure_guild(guild_id)
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
        UPDATE guild_settings
        SET raid_mode = NOT raid_mode
        WHERE guild_id=$1
        RETURNING raid_mode;
        """, guild_id)
        return row["raid_mode"]

async def toggle_lockdown(guild_id):
    await ensure_guild(guild_id)
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
        UPDATE guild_settings
        SET lockdown = NOT lockdown
        WHERE guild_id=$1
        RETURNING lockdown;
        """, guild_id)
        return row["lockdown"]

# ---------------- INFRACTIONS ----------------

async def add_infraction(guild_id, user_id, moderator_id, action, reason):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO infractions (guild_id, user_id, moderator_id, action, reason)
        VALUES ($1,$2,$3,$4,$5);
        """, guild_id, user_id, moderator_id, action, reason)

async def get_user_logs(guild_id, user_id):
    async with pool.acquire() as conn:
        return await conn.fetch("""
        SELECT * FROM infractions
        WHERE guild_id=$1 AND user_id=$2
        ORDER BY created_at DESC
        LIMIT 10;
        """, guild_id, user_id)
