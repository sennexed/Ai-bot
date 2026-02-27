import discord
from discord.ext import commands
from discord import app_commands
from core.database import (
    get_pending_appeals,
    update_appeal,
    resolve_case,
    log_staff_action
)

class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="appeals", description="View pending appeals")
    async def appeals(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message("No permission.", ephemeral=True)

        appeals = await get_pending_appeals(interaction.guild.id)

        if not appeals:
            return await interaction.response.send_message("No pending appeals.")

        msg = "\n".join(
            [f"Appeal ID: {a['id']} | Case: {a['case_id']}" for a in appeals]
        )

        await interaction.response.send_message(msg)

    @app_commands.command(name="appeal_accept")
    async def appeal_accept(self, interaction: discord.Interaction, appeal_id: int):
        await update_appeal(appeal_id, "ACCEPTED")
        await interaction.response.send_message("Appeal accepted.")
        await log_staff_action(interaction.guild.id,
                               interaction.user.id,
                               "APPEAL_ACCEPT",
                               None)

    @app_commands.command(name="appeal_deny")
    async def appeal_deny(self, interaction: discord.Interaction, appeal_id: int):
        await update_appeal(appeal_id, "DENIED")
        await interaction.response.send_message("Appeal denied.")
        await log_staff_action(interaction.guild.id,
                               interaction.user.id,
                               "APPEAL_DENY",
                               None)

async def setup(bot):
    await bot.add_cog(Staff(bot))
