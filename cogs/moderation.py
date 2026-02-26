import discord
import re
import datetime
from discord.ext import commands
from discord import app_commands

from core.database import (
    add_infraction,
    get_user_infractions,
    store_message,
    add_toxicity,
    get_toxicity,
    log_join
)


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # ---------------- SLASH COMMANDS ----------------

    @app_commands.command(name="warn", description="Warn a user")
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):

        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("No permission.", ephemeral=True)
            return

        await add_infraction(
            interaction.guild.id,
            member.id,
            interaction.user.id,
            "warn",
            reason,
            10
        )

        try:
            await member.send(
                f"You were warned in {interaction.guild.name}.\nReason: {reason}"
            )
        except:
            pass

        await interaction.response.send_message(
            f"{member.mention} has been warned."
        )


    @app_commands.command(name="infractions", description="View user infractions")
    async def infractions(self, interaction: discord.Interaction, member: discord.Member):

        rows = await get_user_infractions(
            interaction.guild.id,
            member.id
        )

        if not rows:
            await interaction.response.send_message("No infractions found.")
            return

        desc = ""
        for r in rows[:10]:
            desc += f"• {r['action']} | {r['reason']} | Severity: {r['severity']}\n"

        embed = discord.Embed(
            title=f"{member.name}'s Infractions",
            description=desc,
            color=discord.Color.red()
        )

        await interaction.response.send_message(embed=embed)


    # ---------------- AUTO MODERATION ----------------

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author.bot:
            return

        await store_message(message.guild.id, message.author.id, message.content)

        severity = 0

        if message.content.count("!") > 5:
            severity += 20

        if len(message.mentions) > 5:
            severity += 40

        if re.search(r"(?:\w\s){5,}", message.content):
            severity += 30

        blacklist = ["idiot", "stupid", "kill yourself"]
        for word in blacklist:
            if word in message.content.lower():
                severity += 50

        if severity > 0:
            await add_toxicity(message.guild.id, message.author.id, severity)

        total = await get_toxicity(message.guild.id, message.author.id)

        if severity >= 70 or total > 150:

            await add_infraction(
                message.guild.id,
                message.author.id,
                self.bot.user.id,
                "auto_warn",
                "Automated toxicity detection",
                severity
            )

            try:
                await message.author.send(
                    f"You triggered moderation in {message.guild.name}.\nSeverity: {severity}"
                )
            except:
                pass

            await message.delete()

        await self.bot.process_commands(message)


    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await log_join(member.guild.id, member.id)

        account_age = (datetime.datetime.utcnow() - member.created_at).days

        if account_age < 3:
            try:
                await member.send("Your account is new. Please follow server rules.")
            except:
                pass


async def setup(bot):
    await bot.add_cog(Moderation(bot))
