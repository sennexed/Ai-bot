import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
from core.database import add_infraction, get_infractions
from utils.ai import moderate

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        result = await moderate(message.content)

        if result.startswith("DELETE"):
            reason = result.split("|", 1)[1] if "|" in result else "AI"
            await message.delete()
            await add_infraction(message.guild.id, message.author.id, "delete", reason)

    @app_commands.command(name="timeout")
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, seconds: int):
        await user.timeout(discord.utils.utcnow() + timedelta(seconds=seconds))
        await add_infraction(interaction.guild.id, user.id, "timeout", "Manual timeout", seconds)
        await interaction.response.send_message("User timed out.")

    @app_commands.command(name="infractions")
    async def infractions(self, interaction: discord.Interaction, user: discord.Member):
        records = await get_infractions(interaction.guild.id, user.id)
        if not records:
            return await interaction.response.send_message("No infractions.")

        text = "\n".join([f"{r[0]} | {r[1]}" for r in records])
        await interaction.response.send_message(text)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
