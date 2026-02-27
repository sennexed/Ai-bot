import discord
from discord.ext import commands
from utils.ai import analyze_message, strictness_threshold
from core.database import (
    get_guild_settings,
    add_infraction,
    count_user_infractions
)

class AIManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        settings = await get_guild_settings(message.guild.id)

        if not settings:
            return

        if not settings["ai_enabled"]:
            return

        result = await analyze_message(message.content)

        severity = result["severity"]
        explanation = result["explanation"]

        threshold = strictness_threshold(settings["ai_strictness"])

        if severity < threshold:
            return

        infractions = await count_user_infractions(
            message.guild.id,
            message.author.id
        )

        action = "WARN"

        if infractions >= 3:
            action = "BAN"
        elif infractions == 2:
            action = "TIMEOUT"

        try:

            if action == "WARN":
                await message.author.send(
                    f"You were warned for: {explanation}"
                )

            elif action == "TIMEOUT":
                await message.author.timeout(
                    discord.utils.utcnow() + discord.timedelta(minutes=10)
                )

            elif action == "BAN":
                await message.guild.ban(
                    message.author,
                    reason="AI Auto Ban"
                )

            await add_infraction(
                message.guild.id,
                message.author.id,
                self.bot.user.id,
                action,
                explanation,
                severity,
                explanation
            )

        except:
            pass


async def setup(bot):
    await bot.add_cog(AIManagement(bot))
