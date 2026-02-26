import aiosqlite
import os
import time

DB_PATH = "data/database.db"

async def init_db():
    os.makedirs("data", exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS infractions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id TEXT,
            user_id TEXT,
            moderator_id TEXT,
            action TEXT,
            reason TEXT,
            duration INTEGER,
            timestamp INTEGER
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS guild_settings (
            guild_id TEXT PRIMARY KEY,
            log_channel TEXT,
            panel_channel TEXT,
            ai_enabled INTEGER DEFAULT 1,
            ai_strictness TEXT DEFAULT 'medium'
        )
        """)

        await db.commit()

async def add_infraction(guild_id, user_id, moderator_id, action, reason, duration=None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        INSERT INTO infractions
        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)
        """, (str(guild_id), str(user_id), str(moderator_id),
              action, reason, duration, int(time.time())))
        await db.commit()

async def save_guild_settings(guild_id, log_channel, panel_channel):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        INSERT OR REPLACE INTO guild_settings
        (guild_id, log_channel, panel_channel)
        VALUES (?, ?, ?)
        """, (str(guild_id), str(log_channel), str(panel_channel)))
        await db.commit()

async def get_guild_settings(guild_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
        SELECT log_channel, panel_channel, ai_enabled, ai_strictness
        FROM guild_settings
        WHERE guild_id=?
        """, (str(guild_id),))
        return await cursor.fetchone()

async def toggle_ai(guild_id, value):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        UPDATE guild_settings
        SET ai_enabled=?
        WHERE guild_id=?
        """, (value, str(guild_id)))
        await db.commit()

async def set_ai_strictness(guild_id, level):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        UPDATE guild_settings
        SET ai_strictness=?
        WHERE guild_id=?
        """, (level, str(guild_id)))
        await db.commit()
