import os
import asyncpg

pool = None


# ----------------------------
# INIT DATABASE
# ----------------------------
async def init_db():
    global pool

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL not set")

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
        CREATE TABLE IF NOT EXISTS message_history (
            guild_id BIGINT,
            user_id BIGINT,
            content TEXT,
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

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS join_logs (
            guild_id BIGINT,
            user_id BIGINT,
            joined_at TIMESTAMP DEFAULT NOW()
        );
        """)


# ----------------------------
# INFRACTIONS
# ----------------------------
async def add_infraction(guild_id, user_id, moderator_id, action, reason, severity=1):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO infractions
        (guild_id, user_id, moderator_id, action, reason, severity)
        VALUES ($1,$2,$3,$4,$5,$6);
        """, guild_id, user_id, moderator_id, action, reason, severity)


async def get_user_infractions(guild_id, user_id):
    async with pool.acquire() as conn:
        return await conn.fetch("""
        SELECT * FROM infractions
        WHERE guild_id=$1 AND user_id=$2
        ORDER BY created_at DESC;
        """, guild_id, user_id)


# ----------------------------
# MESSAGE MEMORY
# ----------------------------
async def store_message(guild_id, user_id, content):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO message_history (guild_id, user_id, content)
        VALUES ($1,$2,$3);
        """, guild_id, user_id, content)


async def get_recent_messages(guild_id, user_id, limit=5):
    async with pool.acquire() as conn:
        return await conn.fetch("""
        SELECT content FROM message_history
        WHERE guild_id=$1 AND user_id=$2
        ORDER BY created_at DESC
        LIMIT $3;
        """, guild_id, user_id, limit)


# ----------------------------
# TOXICITY SYSTEM
# ----------------------------
async def add_toxicity(guild_id, user_id, amount):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO toxicity_scores (guild_id, user_id, score)
        VALUES ($1,$2,$3)
        ON CONFLICT (guild_id, user_id)
        DO UPDATE SET score = toxicity_scores.score + $3;
        """, guild_id, user_id, amount)


async def get_toxicity(guild_id, user_id):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
        SELECT score FROM toxicity_scores
        WHERE guild_id=$1 AND user_id=$2;
        """, guild_id, user_id)
        return row["score"] if row else 0


# ----------------------------
# JOIN TRACKING
# ----------------------------
async def log_join(guild_id, user_id):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO join_logs (guild_id, user_id)
        VALUES ($1,$2);
        """, guild_id, user_id)

# ----------------------------
# GUILD SETTINGS
# ----------------------------
async def set_log_channel(guild_id, channel_id):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO guild_settings (guild_id, log_channel)
        VALUES ($1,$2)
        ON CONFLICT (guild_id)
        DO UPDATE SET log_channel=$2;
        """, guild_id, channel_id)


async def get_log_channel(guild_id):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
        SELECT log_channel FROM guild_settings
        WHERE guild_id=$1;
        """, guild_id)
        return row["log_channel"] if row else None


async def toggle_ai(guild_id):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
        SELECT ai_enabled FROM guild_settings
        WHERE guild_id=$1;
        """, guild_id)

        if not row:
            await conn.execute("""
            INSERT INTO guild_settings (guild_id, ai_enabled)
            VALUES ($1, FALSE);
            """, guild_id)
            return False

        new_value = not row["ai_enabled"]

        await conn.execute("""
        UPDATE guild_settings
        SET ai_enabled=$2
        WHERE guild_id=$1;
        """, guild_id, new_value)

        return new_value
