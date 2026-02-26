import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from core.database import init_db

load_dotenv()

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


async def load_cogs():
    try:
        await bot.load_extension("cogs.moderation")
        print("Moderation cog loaded.")
    except Exception as e:
        print(f"Failed to load moderation cog: {e}")
        raise


@bot.event
async def on_ready():
    print(f"Bot ready as {bot.user} (ID: {bot.user.id})")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Slash sync failed: {e}")


@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Unhandled error in event: {event}")


async def main():
    print("Starting bot...")

    await init_db()
    print("Database initialized.")

    await load_cogs()

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN not set.")

    await bot.start(token)


asyncio.run(main())
