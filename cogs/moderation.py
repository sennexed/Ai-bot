import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
from core.database import (
    add_infraction,
    get_guild_settings,
    save_guild_settings,
    toggle_ai,
    set_ai_strictness,
    get_infractions
)
from utils.ai import moderate


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(ControlPanel(bot))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        settings = await get_guild_settings(message.guild.id)
        if not settings:
            return

        ai_enabled = settings[2]
        strictness = settings[3]

        if ai_enabled != 1:
            return

        try:
            result = await moderate(message.content, strictness)
            if isinstance(result, str) and result.startswith("DELETE"):
                await message.delete()
                await add_infraction(
                    message.guild.id,
                    message.author.id,
                    0,
                    "ai-delete",
                    "AI flagged message"
                )
        except:
            pass

    @app_commands.command(name="setup", description="Configure log channel.")
    async def setup(self, interaction: discord.Interaction,
                    log_channel: discord.TextChannel):

        await save_guild_settings(interaction.guild.id, log_channel.id)
        await interaction.response.send_message("Setup complete.", ephemeral=True)

    @app_commands.command(name="panel", description="Open moderation panel.")
    async def panel(self, interaction: discord.Interaction):
        settings = await get_guild_settings(interaction.guild.id)
        if not settings:
            await interaction.response.send_message("Run /setup first.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Moderation Control Panel",
            description="Select user below, then choose action.",
            color=discord.Color.red()
        )

        await interaction.response.send_message(
            embed=embed,
            view=ControlPanel(self.bot)
        )


class UserSelect(discord.ui.UserSelect):
    def __init__(self):
        super().__init__(placeholder="Select a user to moderate",
                         min_values=1,
                         max_values=1)

    async def callback(self, interaction: discord.Interaction):
        interaction.client.selected_user = self.values[0]
        await interaction.response.send_message(
            f"Selected: {self.values[0].mention}",
            ephemeral=True
        )


class ControlPanel(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(UserSelect())

    async def interaction_check(self, interaction):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("No permission.", ephemeral=True)
            return False
        return True

    async def get_target(self, interaction):
        return getattr(self.bot, "selected_user", None)

    @discord.ui.button(label="Warn", style=discord.ButtonStyle.primary)
    async def warn_btn(self, interaction, button):
        target = await self.get_target(interaction)
        if not target:
            await interaction.response.send_message("Select user first.", ephemeral=True)
            return

        await add_infraction(interaction.guild.id,
                             target.id,
                             interaction.user.id,
                             "warn",
                             "Manual warning")
        await interaction.response.send_message("Warning stored.", ephemeral=True)

    @discord.ui.button(label="Kick", style=discord.ButtonStyle.danger)
    async def kick_btn(self, interaction, button):
        target = await self.get_target(interaction)
        if not target:
            await interaction.response.send_message("Select user first.", ephemeral=True)
            return

        try:
            await target.kick()
            await add_infraction(interaction.guild.id,
                                 target.id,
                                 interaction.user.id,
                                 "kick",
                                 "Manual kick")
            await interaction.response.send_message("User kicked.", ephemeral=True)
        except:
            await interaction.response.send_message("Cannot kick user.", ephemeral=True)

    @discord.ui.button(label="Ban", style=discord.ButtonStyle.danger)
    async def ban_btn(self, interaction, button):
        target = await self.get_target(interaction)
        if not target:
            await interaction.response.send_message("Select user first.", ephemeral=True)
            return

        try:
            await target.ban()
            await add_infraction(interaction.guild.id,
                                 target.id,
                                 interaction.user.id,
                                 "ban",
                                 "Manual ban")
            await interaction.response.send_message("User banned.", ephemeral=True)
        except:
            await interaction.response.send_message("Cannot ban user.", ephemeral=True)

    @discord.ui.button(label="Timeout 10m", style=discord.ButtonStyle.secondary)
    async def timeout_btn(self, interaction, button):
        target = await self.get_target(interaction)
        if not target:
            await interaction.response.send_message("Select user first.", ephemeral=True)
            return

        try:
            await target.timeout(discord.utils.utcnow() + timedelta(minutes=10))
            await add_infraction(interaction.guild.id,
                                 target.id,
                                 interaction.user.id,
                                 "timeout",
                                 "10 minute timeout")
            await interaction.response.send_message("User timed out.", ephemeral=True)
        except:
            await interaction.response.send_message("Cannot timeout user.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
