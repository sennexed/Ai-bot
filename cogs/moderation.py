import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
from core.database import (
    add_infraction,
    get_guild_settings,
    save_guild_settings,
    toggle_ai,
    set_ai_strictness
)
from utils.ai import moderate

# ================= PANEL VIEW =================

class AIPanel(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("No permission.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Warn", style=discord.ButtonStyle.primary)
    async def warn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Reply with @user to warn.", ephemeral=True)

    @discord.ui.button(label="Lockdown", style=discord.ButtonStyle.secondary)
    async def lockdown(self, interaction: discord.Interaction, button: discord.ui.Button):
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = False
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message("Channel locked.", ephemeral=True)

    @discord.ui.button(label="Toggle AI", style=discord.ButtonStyle.success)
    async def toggle_ai_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = await get_guild_settings(interaction.guild.id)
        new_state = 0 if settings[2] == 1 else 1
        await toggle_ai(interaction.guild.id, new_state)
        await interaction.response.send_message(f"AI Enabled: {bool(new_state)}", ephemeral=True)

    @discord.ui.button(label="AI Strictness", style=discord.ButtonStyle.secondary)
    async def strictness(self, interaction: discord.Interaction, button: discord.ui.Button):
        await set_ai_strictness(interaction.guild.id, "high")
        await interaction.response.send_message("AI strictness set to HIGH.", ephemeral=True)

# ================= COG =================

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
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
            await add_infraction(message.guild.id, message.author.id, 0, "ai-delete", "AI flagged message")

    @app_commands.command(name="setup", description="Configure bot channels (one-time).")
    async def setup(self, interaction: discord.Interaction,
                    log_channel: discord.TextChannel,
                    panel_channel: discord.TextChannel):

        existing = await get_guild_settings(interaction.guild.id)
        if existing:
            return await interaction.response.send_message("Already configured.", ephemeral=True)

        await save_guild_settings(interaction.guild.id, log_channel.id, panel_channel.id)
        await interaction.response.send_message("Setup complete.", ephemeral=True)

    @app_commands.command(name="panel", description="Open moderation + AI control panel.")
    async def panel(self, interaction: discord.Interaction):

        settings = await get_guild_settings(interaction.guild.id)
        if not settings:
            return await interaction.response.send_message("Run /setup first.", ephemeral=True)

        if interaction.channel.id != int(settings[1]):
            return await interaction.response.send_message("Use this in the configured panel channel.", ephemeral=True)

        embed = discord.Embed(
            title="Moderation Control Panel",
            description="Manage server and AI settings below.",
            color=discord.Color.red()
        )

        await interaction.response.send_message(embed=embed, view=AIPanel(self.bot))

async def setup(bot):
    await bot.add_cog(Moderation(bot))
EOFcat << 'EOF' > cogs/moderation.py
import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
from core.database import (
    add_infraction,
    get_guild_settings,
    save_guild_settings,
    toggle_ai,
    set_ai_strictness
)
from utils.ai import moderate

# ================= PANEL VIEW =================

class AIPanel(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("No permission.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Warn", style=discord.ButtonStyle.primary)
    async def warn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Reply with @user to warn.", ephemeral=True)

    @discord.ui.button(label="Lockdown", style=discord.ButtonStyle.secondary)
    async def lockdown(self, interaction: discord.Interaction, button: discord.ui.Button):
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = False
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message("Channel locked.", ephemeral=True)

    @discord.ui.button(label="Toggle AI", style=discord.ButtonStyle.success)
    async def toggle_ai_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = await get_guild_settings(interaction.guild.id)
        new_state = 0 if settings[2] == 1 else 1
        await toggle_ai(interaction.guild.id, new_state)
        await interaction.response.send_message(f"AI Enabled: {bool(new_state)}", ephemeral=True)

    @discord.ui.button(label="AI Strictness", style=discord.ButtonStyle.secondary)
    async def strictness(self, interaction: discord.Interaction, button: discord.ui.Button):
        await set_ai_strictness(interaction.guild.id, "high")
        await interaction.response.send_message("AI strictness set to HIGH.", ephemeral=True)

# ================= COG =================

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
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
            await add_infraction(message.guild.id, message.author.id, 0, "ai-delete", "AI flagged message")

    @app_commands.command(name="setup", description="Configure bot channels (one-time).")
    async def setup(self, interaction: discord.Interaction,
                    log_channel: discord.TextChannel,
                    panel_channel: discord.TextChannel):

        existing = await get_guild_settings(interaction.guild.id)
        if existing:
            return await interaction.response.send_message("Already configured.", ephemeral=True)

        await save_guild_settings(interaction.guild.id, log_channel.id, panel_channel.id)
        await interaction.response.send_message("Setup complete.", ephemeral=True)

    @app_commands.command(name="panel", description="Open moderation + AI control panel.")
    async def panel(self, interaction: discord.Interaction):

        settings = await get_guild_settings(interaction.guild.id)
        if not settings:
            return await interaction.response.send_message("Run /setup first.", ephemeral=True)

        if interaction.channel.id != int(settings[1]):
            return await interaction.response.send_message("Use this in the configured panel channel.", ephemeral=True)

        embed = discord.Embed(
            title="Moderation Control Panel",
            description="Manage server and AI settings below.",
            color=discord.Color.red()
        )

        await interaction.response.send_message(embed=embed, view=AIPanel(self.bot))

async def setup(bot):
    await bot.add_cog(Moderation(bot))
