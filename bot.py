import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from core.database import init_db

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


async def load_cogs():
    await bot.load_extension("cogs.moderation")


@bot.event
async def on_ready():
    print(f"Bot ready as {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Slash sync failed: {e}")


async def main():
    print("Initializing database...")
    await init_db()
    print("Database initialized.")

    await load_cogs()

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN is missing.")

    await bot.start(token)


asyncio.run(main())
