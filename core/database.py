import os
import asyncpg

pool = None


async def init_db():
    global pool

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL not set")

    pool = await asyncpg.create_pool(
        database_url,
        min_size=1,
        max_size=5
    )

    async with pool.acquire() as conn:

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS guild_settings (
            guild_id BIGINT PRIMARY KEY,
            log_channel BIGINT,
            ai_enabled BOOLEAN DEFAULT TRUE
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
            severity INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS toxicity_scores (
            guild_id BIGINT,
            user_id BIGINT,
            score INTEGER DEFAULT 0,
            PRIMARY KEY (guild_id, user_id)
        );
        """)


# ---------- SAFE HELPERS ----------

async def add_infraction(guild_id, user_id, moderator_id, action, reason, severity=1):
    if not pool:
        return

    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO infractions
        (guild_id, user_id, moderator_id, action, reason, severity)
        VALUES ($1,$2,$3,$4,$5,$6);
        """, guild_id, user_id, moderator_id, action, reason, severity)


async def get_user_infractions(guild_id, user_id):
    if not pool:
        return []

    async with pool.acquire() as conn:
        return await conn.fetch("""
        SELECT * FROM infractions
        WHERE guild_id=$1 AND user_id=$2
        ORDER BY created_at DESC;
        """, guild_id, user_id)


async def add_toxicity(guild_id, user_id, amount):
    if not pool:
        return

    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO toxicity_scores (guild_id, user_id, score)
        VALUES ($1,$2,$3)
        ON CONFLICT (guild_id, user_id)
        DO UPDATE SET score = toxicity_scores.score + $3;
        """, guild_id, user_id, amount)


async def get_toxicity(guild_id, user_id):
    if not pool:
        return 0

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
        SELECT score FROM toxicity_scores
        WHERE guild_id=$1 AND user_id=$2;
        """, guild_id, user_id)

        return row["score"] if row else 0
