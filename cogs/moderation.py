import discord
from discord.ext import commands
from discord import app_commands
from core.database import (
    set_log_channel,
    toggle_ai,
    toggle_raid,
    toggle_lockdown,
    add_infraction,
    get_user_logs
)

# ===========================
# MODERATION PANEL
# ===========================

class ModerationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Warn", style=discord.ButtonStyle.primary, custom_id="mod_warn")
    async def warn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Mention a user to warn.", ephemeral=True)

    @discord.ui.button(label="Kick", style=discord.ButtonStyle.secondary, custom_id="mod_kick")
    async def kick(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Kick system ready.", ephemeral=True)

    @discord.ui.button(label="Ban", style=discord.ButtonStyle.danger, custom_id="mod_ban")
    async def ban(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ban system ready.", ephemeral=True)

# ===========================
# AI PANEL
# ===========================

class AIView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Toggle AI", style=discord.ButtonStyle.success, custom_id="ai_toggle")
    async def toggle_ai_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        state = await toggle_ai(interaction.guild.id)
        await interaction.response.send_message(f"AI Enabled: {state}", ephemeral=True)

# ===========================
# SECURITY PANEL
# ===========================

class SecurityView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Raid Mode", style=discord.ButtonStyle.danger, custom_id="sec_raid")
    async def raid(self, interaction: discord.Interaction, button: discord.ui.Button):
        state = await toggle_raid(interaction.guild.id)
        await interaction.response.send_message(f"Raid Mode: {state}", ephemeral=True)

    @discord.ui.button(label="Lockdown", style=discord.ButtonStyle.secondary, custom_id="sec_lock")
    async def lockdown(self, interaction: discord.Interaction, button: discord.ui.Button):
        state = await toggle_lockdown(interaction.guild.id)
        await interaction.response.send_message(f"Lockdown: {state}", ephemeral=True)

# ===========================
# DETECTION PANEL
# ===========================

class DetectionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Keyword System", style=discord.ButtonStyle.primary, custom_id="det_keyword")
    async def keyword(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Keyword system active.", ephemeral=True)

# ===========================
# ANALYTICS PANEL
# ===========================

class AnalyticsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Server Stats", style=discord.ButtonStyle.secondary, custom_id="analytics_stats")
    async def stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Analytics system active.", ephemeral=True)

# ===========================
# LOGS PANEL
# ===========================

class LogsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="View User Logs", style=discord.ButtonStyle.primary, custom_id="logs_user")
    async def logs(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Use /logs user", ephemeral=True)

# ===========================
# SETTINGS PANEL
# ===========================

class SettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="System Settings", style=discord.ButtonStyle.secondary, custom_id="settings_main")
    async def settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Settings active.", ephemeral=True)

# ===========================
# COG
# ===========================

class Control(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(ModerationView())
        bot.add_view(AIView())
        bot.add_view(SecurityView())
        bot.add_view(DetectionView())
        bot.add_view(AnalyticsView())
        bot.add_view(LogsView())
        bot.add_view(SettingsView())

    # ---------- SETUP ----------
    @app_commands.command(name="setup", description="Set log channel")
    async def setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Admin only.", ephemeral=True)
            return
        await set_log_channel(interaction.guild.id, channel.id)
        await interaction.response.send_message("Log channel set.", ephemeral=True)

    # ---------- CATEGORY COMMANDS ----------
    @app_commands.command(name="moderation", description="Open moderation panel")
    async def moderation(self, interaction: discord.Interaction):
        await interaction.response.send_message("Moderation Panel", view=ModerationView())

    @app_commands.command(name="ai", description="Open AI panel")
    async def ai(self, interaction: discord.Interaction):
        await interaction.response.send_message("AI Panel", view=AIView())

    @app_commands.command(name="security", description="Open security panel")
    async def security(self, interaction: discord.Interaction):
        await interaction.response.send_message("Security Panel", view=SecurityView())

    @app_commands.command(name="detection", description="Open detection panel")
    async def detection(self, interaction: discord.Interaction):
        await interaction.response.send_message("Detection Panel", view=DetectionView())

    @app_commands.command(name="analytics", description="Open analytics panel")
    async def analytics(self, interaction: discord.Interaction):
        await interaction.response.send_message("Analytics Panel", view=AnalyticsView())

    @app_commands.command(name="logs", description="Open logs panel")
    async def logs(self, interaction: discord.Interaction):
        await interaction.response.send_message("Logs Panel", view=LogsView())

    @app_commands.command(name="settings", description="Open settings panel")
    async def settings(self, interaction: discord.Interaction):
        await interaction.response.send_message("Settings Panel", view=SettingsView())

async def setup(bot):
    await bot.add_cog(Control(bot))
