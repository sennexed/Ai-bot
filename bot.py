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
    await bot.load_extension("cogs.management")
    await bot.load_extension("cogs.moderation")
    await bot.load_extension("cogs.security")

@bot.event
async def on_ready():
    await init_db()
    await bot.tree.sync()
    print(f"Bot ready as {bot.user}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("DISCORD_TOKEN"))

asyncio.run(main())
