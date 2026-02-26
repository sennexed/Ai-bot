import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
from core.database import add_infraction, get_infractions, count_warnings

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------------------------
    # BASIC ACTIONS
    # ---------------------------

    @app_commands.command(name="warn")
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason"):
        await add_infraction(interaction.guild.id, user.id, interaction.user.id, "warn", reason)
        warns = await count_warnings(interaction.guild.id, user.id)

        if warns >= 3:
            await user.timeout(discord.utils.utcnow() + timedelta(hours=1))
            await add_infraction(interaction.guild.id, user.id, interaction.user.id, "auto-timeout", "3 warnings", 3600)

        await interaction.response.send_message(f"{user.mention} warned. Total warnings: {warns}")

    @app_commands.command(name="timeout")
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, seconds: int, reason: str = "No reason"):
        await user.timeout(discord.utils.utcnow() + timedelta(seconds=seconds))
        await add_infraction(interaction.guild.id, user.id, interaction.user.id, "timeout", reason, seconds)
        await interaction.response.send_message("User timed out.")

    @app_commands.command(name="kick")
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason"):
        await user.kick(reason=reason)
        await add_infraction(interaction.guild.id, user.id, interaction.user.id, "kick", reason)
        await interaction.response.send_message("User kicked.")

    @app_commands.command(name="ban")
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason"):
        await user.ban(reason=reason)
        await add_infraction(interaction.guild.id, user.id, interaction.user.id, "ban", reason)
        await interaction.response.send_message("User banned.")

    @app_commands.command(name="unban")
    async def unban(self, interaction: discord.Interaction, user_id: str):
        user = await self.bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        await interaction.response.send_message("User unbanned.")

    # ---------------------------
    # INFO
    # ---------------------------

    @app_commands.command(name="infractions")
    async def infractions(self, interaction: discord.Interaction, user: discord.Member):
        records = await get_infractions(interaction.guild.id, user.id)
        if not records:
            return await interaction.response.send_message("No infractions.")

        text = "\n".join([f"{r[0]} | {r[1]}" for r in records[:10]])
        await interaction.response.send_message(text)

    @app_commands.command(name="clearinfractions")
    async def clearinfractions(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.send_message("Manual clearing not implemented yet.")

    # ---------------------------
    # CLEANUP
    # ---------------------------

    @app_commands.command(name="purge")
    async def purge(self, interaction: discord.Interaction, amount: int):
        await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"Deleted {amount} messages.", ephemeral=True)

    @app_commands.command(name="slowmode")
    async def slowmode(self, interaction: discord.Interaction, seconds: int):
        await interaction.channel.edit(slowmode_delay=seconds)
        await interaction.response.send_message("Slowmode updated.")

    # ---------------------------
    # WHOIS
    # ---------------------------

    @app_commands.command(name="whois")
    async def whois(self, interaction: discord.Interaction, user: discord.Member):
        embed = discord.Embed(title="User Info")
        embed.add_field(name="ID", value=user.id)
        embed.add_field(name="Joined", value=user.joined_at)
        embed.add_field(name="Created", value=user.created_at)
        embed.add_field(name="Roles", value=", ".join([r.name for r in user.roles]))
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
