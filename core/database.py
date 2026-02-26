import aiosqlite
import os

DB_PATH = "data/database.db"

async def init_db():
    os.makedirs("data", exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS infractions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id TEXT,
            user_id TEXT,
            action TEXT,
            reason TEXT,
            duration INTEGER,
            timestamp INTEGER DEFAULT (strftime('%s','now'))
        )
        """)
        await db.commit()

async def add_infraction(guild_id, user_id, action, reason, duration=None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        INSERT INTO infractions 
        (guild_id, user_id, action, reason, duration)
        VALUES (?, ?, ?, ?, ?)
        """, (str(guild_id), str(user_id), action, reason, duration))
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
