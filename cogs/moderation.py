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


class ControlPanel(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("No permission.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Warn", style=discord.ButtonStyle.primary)
    async def warn_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await add_infraction(interaction.guild.id, interaction.user.id,
                             interaction.user.id, "warn", "Panel warning")
        await interaction.response.send_message("Warning stored.", ephemeral=True)

    @discord.ui.button(label="Kick", style=discord.ButtonStyle.danger)
    async def kick_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.user.kick()
        await add_infraction(interaction.guild.id, interaction.user.id,
                             interaction.user.id, "kick", "Panel kick")
        await interaction.response.send_message("User kicked.", ephemeral=True)

    @discord.ui.button(label="Ban", style=discord.ButtonStyle.danger)
    async def ban_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.user.ban()
        await add_infraction(interaction.guild.id, interaction.user.id,
                             interaction.user.id, "ban", "Panel ban")
        await interaction.response.send_message("User banned.", ephemeral=True)

    @discord.ui.button(label="Timeout 10m", style=discord.ButtonStyle.secondary)
    async def timeout_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.user.timeout(
            discord.utils.utcnow() + timedelta(minutes=10)
        )
        await add_infraction(interaction.guild.id, interaction.user.id,
                             interaction.user.id, "timeout", "10m timeout")
        await interaction.response.send_message("Timed out 10m.", ephemeral=True)

    @discord.ui.button(label="Lock Channel", style=discord.ButtonStyle.secondary)
    async def lock_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = False
        await interaction.channel.set_permissions(
            interaction.guild.default_role, overwrite=overwrite
        )
        await interaction.response.send_message("Channel locked.", ephemeral=True)

    @discord.ui.button(label="Slowmode 10s", style=discord.ButtonStyle.secondary)
    async def slow_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.edit(slowmode_delay=10)
        await interaction.response.send_message("Slowmode set.", ephemeral=True)

    @discord.ui.button(label="Toggle AI", style=discord.ButtonStyle.success)
    async def toggle_ai_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = await get_guild_settings(interaction.guild.id)
        new_state = 0 if settings[2] == 1 else 1
        await toggle_ai(interaction.guild.id, new_state)
        await interaction.response.send_message(f"AI Enabled: {bool(new_state)}", ephemeral=True)

    @discord.ui.button(label="Cycle AI Strictness", style=discord.ButtonStyle.secondary)
    async def strict_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = await get_guild_settings(interaction.guild.id)
        current = settings[3]
        new = "low" if current == "high" else "medium" if current == "low" else "high"
        await set_ai_strictness(interaction.guild.id, new)
        await interaction.response.send_message(f"Strictness: {new}", ephemeral=True)

    @discord.ui.button(label="View Warnings", style=discord.ButtonStyle.primary)
    async def view_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        records = await get_infractions(interaction.guild.id, interaction.user.id)
        if not records:
            await interaction.response.send_message("No warnings.", ephemeral=True)
            return

        text = "\n".join(
            [f"{r[0]} | {r[1]} | {r[2]}" for r in records[:5]]
        )
        await interaction.response.send_message(text, ephemeral=True)


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

        result = await moderate(message.content, strictness)

        if result.startswith("DELETE"):
            await message.delete()
            await add_infraction(message.guild.id,
                                 message.author.id,
                                 0,
                                 "ai-delete",
                                 "AI flagged message")

    @app_commands.command(name="setup",
                          description="Configure log channel (one-time).")
    async def setup(self, interaction: discord.Interaction,
                    log_channel: discord.TextChannel):

        existing = await get_guild_settings(interaction.guild.id)
        if existing:
            await interaction.response.send_message("Already configured.", ephemeral=True)
            return

        await save_guild_settings(interaction.guild.id, log_channel.id)
        await interaction.response.send_message("Setup complete.", ephemeral=True)
    @app_commands.command(name="panel",
                          description="Open moderation + AI panel.")
    async def panel(self, interaction: discord.Interaction):

        settings = await get_guild_settings(interaction.guild.id)
        if not settings:
            await interaction.response.send_message("Run /setup first.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Moderation Control Panel",
            description="Persistent S-Tier Controls",
            color=discord.Color.red()
        )

        await interaction.response.send_message(
            embed=embed,
            view=ControlPanel(self.bot)
        )


async def setup(bot):
    await bot.add_cog(Moderation(bot))
