import discord
import json
from datetime import timedelta
from discord.ext import commands
from utils.basic_filters import *
from utils.reputation import *
from utils.ai import moderate
from core.database import (
    add_infraction,
    get_user_reputation,
    set_user_reputation,
    get_user_infractions
)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        # ===== BASIC FILTER LAYER =====

        if is_spam(message.author.id):
            await message.delete()
            return

        if excessive_mentions(message):
            await message.delete()
            return

        if repeated_text(message.content):
            await message.delete()
            return

        if character_flood(message.content):
            await message.delete()
            return

        if contains_blacklisted_link(message.content):
            await message.delete()
            return

        # ===== AI LAYER =====

        try:
            ai_response = await moderate(message.content, 1)

            # Expecting AI to return valid JSON
            data = json.loads(ai_response)

            severity = data.get("toxicity", 0)
            explanation = data.get("explanation", "AI violation detected")

            reputation = await get_user_reputation(
                message.guild.id,
                message.author.id
            )

            infractions = await get_user_infractions(
                message.guild.id,
                message.author.id
            )

            action = calculate_action(severity, len(infractions))

            if not action:
                return

            # Store infraction
            await add_infraction(
                message.guild.id,
                message.author.id,
                0,
                action,
                explanation,
                severity
            )

            # Update reputation
            new_rep = update_reputation(reputation, severity)

            await set_user_reputation(
                message.guild.id,
                message.author.id,
                new_rep
            )

            # Execute punishment
            if action == "warn":
                await message.channel.send(
                    f"{message.author.mention} has been warned."
                )

            elif action == "timeout":
                await message.author.timeout(
                    discord.utils.utcnow() + timedelta(minutes=10)
                )

            elif action == "ban":
                await message.guild.ban(message.author)

        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(Moderation(bot))
