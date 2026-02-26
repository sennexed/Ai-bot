import discord
import datetime
from discord.ext import commands
from discord import app_commands
from core.database import (
    add_infraction,
    get_user_infractions,
    add_toxicity,
    get_toxicity
)


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # ---------- WARN ----------
    @app_commands.command(name="warn", description="Warn a user")
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):

        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("Missing permission.", ephemeral=True)
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
                f"You were warned in {interaction.guild.name}\nReason: {reason}"
            )
        except:
            pass

        await interaction.response.send_message(f"{member.mention} warned.")


    # ---------- MUTE ----------
    @app_commands.command(name="mute", description="Timeout a user")
    async def mute(self, interaction: discord.Interaction, member: discord.Member, minutes: int):

        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("Missing permission.", ephemeral=True)
            return

        until = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)

        try:
            await member.timeout(until)
        except Exception as e:
            await interaction.response.send_message(f"Failed: {e}", ephemeral=True)
            return

        await interaction.response.send_message(
            f"{member.mention} muted for {minutes} minutes."
        )


    # ---------- BAN ----------
    @app_commands.command(name="ban", description="Ban a user")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str):

        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("Missing permission.", ephemeral=True)
            return

        try:
            await member.ban(reason=reason)
        except Exception as e:
            await interaction.response.send_message(f"Failed: {e}", ephemeral=True)
            return

        await add_infraction(
            interaction.guild.id,
            member.id,
            interaction.user.id,
            "ban",
            reason,
            50
        )

        await interaction.response.send_message(f"{member.mention} banned.")


    # ---------- INFRACTIONS ----------
    @app_commands.command(name="infractions", description="View infractions")
    async def infractions(self, interaction: discord.Interaction, member: discord.Member):

        rows = await get_user_infractions(
            interaction.guild.id,
            member.id
        )

        if not rows:
            await interaction.response.send_message("No infractions.")
            return

        desc = ""
        for r in rows[:10]:
            desc += f"{r['action']} | {r['reason']} | Severity {r['severity']}\n"

        embed = discord.Embed(
            title=f"{member.name}'s Infractions",
            description=desc,
            color=discord.Color.red()
        )

        await interaction.response.send_message(embed=embed)


    # ---------- TOXICITY ----------
    @app_commands.command(name="toxicity", description="Check toxicity score")
    async def toxicity(self, interaction: discord.Interaction, member: discord.Member):

        score = await get_toxicity(interaction.guild.id, member.id)

        await interaction.response.send_message(f"Toxicity score: {score}")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
