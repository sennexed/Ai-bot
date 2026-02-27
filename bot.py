import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from core.database import init_db

# =========================
# LOAD ENV
# =========================

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not found in environment variables.")

# =========================
# INTENTS
# =========================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# =========================
# BOT SETUP
# =========================

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================
# LOAD COGS
# =========================

COGS = [
    "cogs.moderation",
    "cogs.management",
    "cogs.security",
    "cogs.info",
    "cogs.staff"
]

async def load_cogs():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"Loaded {cog}")
        except Exception as e:
            print(f"Failed to load {cog}: {e}")

# =========================
# READY EVENT
# =========================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    try:
        await bot.tree.sync()
        print("Slash commands synced globally.")
    except Exception as e:
        print(f"Slash sync failed: {e}")

# =========================
# STARTUP
# =========================

async def main():
    await init_db()  # Initialize Postgres before bot starts

    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
