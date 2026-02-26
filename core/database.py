import aiosqlite
import os

DB_PATH = "data/database.db"
os.makedirs("data", exist_ok=True)


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS guild_settings (
            guild_id INTEGER PRIMARY KEY,
            log_channel INTEGER,
            ai_enabled INTEGER DEFAULT 0,
            ai_strictness TEXT DEFAULT 'medium'
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS infractions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            user_id INTEGER,
            moderator_id INTEGER,
            action TEXT,
            reason TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        await db.commit()


async def save_guild_settings(guild_id, log_channel):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        INSERT OR REPLACE INTO guild_settings (guild_id, log_channel)
        VALUES (?, ?)
        """, (guild_id, log_channel))
        await db.commit()


async def get_guild_settings(guild_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT * FROM guild_settings WHERE guild_id = ?",
            (guild_id,)
        ) as cursor:
            return await cursor.fetchone()


async def toggle_ai(guild_id, state):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        UPDATE guild_settings SET ai_enabled = ?
        WHERE guild_id = ?
        """, (state, guild_id))
        await db.commit()


async def set_ai_strictness(guild_id, level):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        UPDATE guild_settings SET ai_strictness = ?
        WHERE guild_id = ?
        """, (level, guild_id))
        await db.commit()


async def add_infraction(guild_id, user_id, moderator_id, action, reason):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        INSERT INTO infractions (guild_id, user_id, moderator_id, action, reason)
        VALUES (?, ?, ?, ?, ?)
        """, (guild_id, user_id, moderator_id, action, reason))
        await db.commit()


async def get_infractions(guild_id, user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
        SELECT action, reason, timestamp
        FROM infractions
        WHERE guild_id = ? AND user_id = ?
        ORDER BY id DESC
        """, (guild_id, user_id)) as cursor:
            return await cursor.fetchall()
