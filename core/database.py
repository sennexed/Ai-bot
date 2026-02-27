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
            ai_strictness INTEGER DEFAULT 3,
            raid_mode BOOLEAN DEFAULT FALSE,
            lockdown BOOLEAN DEFAULT FALSE,
            antispam BOOLEAN DEFAULT TRUE,
            antilink BOOLEAN DEFAULT TRUE
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

async def get_guild_settings(guild_id):
    async with pool.acquire() as conn:
        return await conn.fetchrow("""
        SELECT * FROM guild_settings WHERE guild_id=$1;
        """, guild_id)

async def toggle_setting(guild_id, field):
    await ensure_guild(guild_id)
    async with pool.acquire() as conn:
        row = await conn.fetchrow(f"""
        UPDATE guild_settings
        SET {field} = NOT {field}
        WHERE guild_id=$1
        RETURNING {field};
        """, guild_id)
        return row[field]

async def get_log_channel(guild_id):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
        SELECT log_channel FROM guild_settings WHERE guild_id=$1;
        """, guild_id)
        return row["log_channel"] if row else None

async def add_infraction(guild_id, user_id, moderator_id, action, reason, severity, explanation):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO infractions
        (guild_id, user_id, moderator_id, action, reason, severity, explanation)
        VALUES ($1,$2,$3,$4,$5,$6,$7);
        """, guild_id, user_id, moderator_id, action, reason, severity, explanation)
