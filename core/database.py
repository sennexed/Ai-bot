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
        await db.commit()

async def add_infraction(guild_id, user_id, moderator_id, action, reason, duration=None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        INSERT INTO infractions
        (guild_id, user_id, moderator_id, action, reason, duration, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (str(guild_id), str(user_id), str(moderator_id), action, reason, duration, int(time.time())))
        await db.commit()

async def get_infractions(guild_id, user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
        SELECT action, reason, duration, timestamp
        FROM infractions
        WHERE guild_id=? AND user_id=?
        ORDER BY timestamp DESC
        """, (str(guild_id), str(user_id)))
        return await cursor.fetchall()

async def count_warnings(guild_id, user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
        SELECT COUNT(*) FROM infractions
        WHERE guild_id=? AND user_id=? AND action='warn'
        """, (str(guild_id), str(user_id)))
        result = await cursor.fetchone()
        return result[0]
