import os
import asyncpg

pool = None

# =========================
# INIT
# =========================

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

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS reputation (
            guild_id BIGINT,
            user_id BIGINT,
            score INTEGER DEFAULT 100,
            PRIMARY KEY (guild_id, user_id)
        );
        """)

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

# =========================
# SETTINGS
# =========================

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
        SELECT * FROM guild_settings
        WHERE guild_id=$1;
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

# =========================
# INFRACTIONS
# =========================

async def add_infraction(guild_id, user_id, moderator_id, action, reason, severity, explanation):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
        INSERT INTO infractions
        (guild_id, user_id, moderator_id, action, reason, severity, explanation)
        VALUES ($1,$2,$3,$4,$5,$6,$7)
        RETURNING id;
        """, guild_id, user_id, moderator_id, action, reason, severity, explanation)

    await decrease_reputation(guild_id, user_id, severity)
    return row["id"]

async def get_case(case_id):
    async with pool.acquire() as conn:
        return await conn.fetchrow("""
        SELECT * FROM infractions WHERE id=$1;
        """, case_id)

async def get_user_cases(guild_id, user_id):
    async with pool.acquire() as conn:
        return await conn.fetch("""
        SELECT * FROM infractions
        WHERE guild_id=$1 AND user_id=$2
        ORDER BY created_at DESC
        LIMIT 10;
        """, guild_id, user_id)

async def count_user_infractions(guild_id, user_id):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
        SELECT COUNT(*) FROM infractions
        WHERE guild_id=$1 AND user_id=$2;
        """, guild_id, user_id)
        return row["count"]

# =========================
# REPUTATION
# =========================

async def decrease_reputation(guild_id, user_id, severity):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO reputation (guild_id, user_id, score)
        VALUES ($1,$2,100)
        ON CONFLICT (guild_id, user_id) DO NOTHING;
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

async def get_top_risk(guild_id):
    async with pool.acquire() as conn:
        return await conn.fetch("""
        SELECT user_id, score
        FROM reputation
        WHERE guild_id=$1
        ORDER BY score ASC
        LIMIT 5;
        """, guild_id)

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
