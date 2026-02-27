import os
import asyncpg
from datetime import datetime, timedelta

pool = None

# =========================
# INIT
# =========================

async def init_db():
    global pool
    pool = await asyncpg.create_pool(os.getenv("DATABASE_URL"))

    async with pool.acquire() as conn:

        # GUILD SETTINGS
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS guild_settings (
            guild_id BIGINT PRIMARY KEY,
            log_channel BIGINT,
            ai_enabled BOOLEAN DEFAULT TRUE,
            ai_strictness INTEGER DEFAULT 3,
            raid_mode BOOLEAN DEFAULT FALSE,
            lockdown BOOLEAN DEFAULT FALSE
        );
        """)

        # MESSAGE MEMORY (Persistent Context)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS message_memory (
            id SERIAL PRIMARY KEY,
            guild_id BIGINT,
            user_id BIGINT,
            content TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

        # INFRACTIONS
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS infractions (
            id SERIAL PRIMARY KEY,
            guild_id BIGINT,
            user_id BIGINT,
            moderator_id BIGINT,
            action TEXT,
            reason TEXT,
            severity INTEGER,
            confidence FLOAT,
            explanation TEXT,
            resolved BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

        # REPUTATION
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS reputation (
            guild_id BIGINT,
            user_id BIGINT,
            score INTEGER DEFAULT 100,
            PRIMARY KEY (guild_id, user_id)
        );
        """)

        # APPEALS
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS appeals (
            id SERIAL PRIMARY KEY,
            guild_id BIGINT,
            case_id INTEGER,
            user_id BIGINT,
            reason TEXT,
            status TEXT DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

        # STAFF AUDIT TRAIL
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS staff_actions (
            id SERIAL PRIMARY KEY,
            guild_id BIGINT,
            moderator_id BIGINT,
            action TEXT,
            case_id INTEGER,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

# =========================
# MESSAGE MEMORY
# =========================

async def store_message(guild_id, user_id, content):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO message_memory (guild_id, user_id, content)
        VALUES ($1,$2,$3);
        """, guild_id, user_id, content)

        # Keep only last 15 messages per user
        await conn.execute("""
        DELETE FROM message_memory
        WHERE id NOT IN (
            SELECT id FROM message_memory
            WHERE guild_id=$1 AND user_id=$2
            ORDER BY created_at DESC
            LIMIT 15
        ) AND guild_id=$1 AND user_id=$2;
        """, guild_id, user_id)

async def get_context(guild_id, user_id):
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
        SELECT content FROM message_memory
        WHERE guild_id=$1 AND user_id=$2
        ORDER BY created_at ASC;
        """, guild_id, user_id)
        return " ".join([r["content"] for r in rows])
# =========================
# SINGLE CASE FETCH
# =========================

async def get_case(case_id):
    async with pool.acquire() as conn:
        return await conn.fetchrow("""
        SELECT * FROM infractions
        WHERE id=$1;
        """, case_id)
# =========================
# INFRACTIONS
# =========================

async def add_infraction(guild_id, user_id, moderator_id, action,
                         reason, severity, confidence, explanation):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
        INSERT INTO infractions
        (guild_id, user_id, moderator_id, action,
         reason, severity, confidence, explanation)
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
        RETURNING id;
        """, guild_id, user_id, moderator_id,
             action, reason, severity, confidence, explanation)

    await decrease_reputation(guild_id, user_id, severity)
    return row["id"]

async def resolve_case(case_id):
    async with pool.acquire() as conn:
        await conn.execute("""
        UPDATE infractions
        SET resolved=TRUE
        WHERE id=$1;
        """, case_id)

# =========================
# REPUTATION
# =========================

async def decrease_reputation(guild_id, user_id, severity):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO reputation (guild_id, user_id)
        VALUES ($1,$2)
        ON CONFLICT DO NOTHING;
        """, guild_id, user_id)

        await conn.execute("""
        UPDATE reputation
        SET score = score - $1
        WHERE guild_id=$2 AND user_id=$3;
        """, severity // 5, guild_id, user_id)

async def get_reputation(guild_id, user_id):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
        SELECT score FROM reputation
        WHERE guild_id=$1 AND user_id=$2;
        """, guild_id, user_id)
        return row["score"] if row else 100

# =========================
# APPEALS
# =========================

async def create_appeal(guild_id, case_id, user_id, reason):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO appeals (guild_id, case_id, user_id, reason)
        VALUES ($1,$2,$3,$4);
        """, guild_id, case_id, user_id, reason)

async def get_pending_appeals(guild_id):
    async with pool.acquire() as conn:
        return await conn.fetch("""
        SELECT * FROM appeals
        WHERE guild_id=$1 AND status='PENDING';
        """, guild_id)

async def update_appeal(appeal_id, status):
    async with pool.acquire() as conn:
        await conn.execute("""
        UPDATE appeals SET status=$1 WHERE id=$2;
        """, status, appeal_id)

# =========================
# STAFF AUDIT
# =========================

async def log_staff_action(guild_id, moderator_id, action, case_id):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO staff_actions
        (guild_id, moderator_id, action, case_id)
        VALUES ($1,$2,$3,$4);
        """, guild_id, moderator_id, action, case_id)
