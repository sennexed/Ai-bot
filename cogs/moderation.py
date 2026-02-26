import discord
from discord.ext import commands
from discord import app_commands
from core.database import set_log_channel, toggle_ai


# ==============================
# AI PANEL
# ==============================

class AIPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Toggle AI", style=discord.ButtonStyle.success, custom_id="ai_toggle")
    async def toggle(self, interaction: discord.Interaction, button: discord.ui.Button):
        state = await toggle_ai(interaction.guild.id)
        await interaction.response.send_message(f"AI Enabled: {state}", ephemeral=True)


# ==============================
# MODERATION PANEL
# ==============================

class ModerationPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Warn", style=discord.ButtonStyle.primary, custom_id="mod_warn")
    async def warn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Use /warn command.", ephemeral=True)

    @discord.ui.button(label="Mute", style=discord.ButtonStyle.secondary, custom_id="mod_mute")
    async def mute(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Use /mute command.", ephemeral=True)

    @discord.ui.button(label="Ban", style=discord.ButtonStyle.danger, custom_id="mod_ban")
    async def ban(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Use /ban command.", ephemeral=True)


# ==============================
# SECURITY PANEL
# ==============================

class SecurityPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Raid Mode", style=discord.ButtonStyle.danger, custom_id="sec_raid")
    async def raid(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Raid system coming soon.", ephemeral=True)


# ==============================
# DETECTION PANEL
# ==============================

class DetectionPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Keyword Filters", style=discord.ButtonStyle.primary, custom_id="det_keywords")
    async def keywords(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Keyword system coming soon.", ephemeral=True)


# ==============================
# MAIN PANEL
# ==============================

class MainPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="AI Panel", style=discord.ButtonStyle.success, custom_id="main_ai")
    async def ai_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="AI Panel", color=discord.Color.green())
        await interaction.response.send_message(embed=embed, view=AIPanel(), ephemeral=True)

    @discord.ui.button(label="Moderation Panel", style=discord.ButtonStyle.primary, custom_id="main_mod")
    async def mod_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Moderation Panel", color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed, view=ModerationPanel(), ephemeral=True)

    @discord.ui.button(label="Security Panel", style=discord.ButtonStyle.danger, custom_id="main_sec")
    async def sec_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Security Panel", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, view=SecurityPanel(), ephemeral=True)

    @discord.ui.button(label="Detection Panel", style=discord.ButtonStyle.secondary, custom_id="main_det")
    async def det_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Detection Panel", color=discord.Color.orange())
        await interaction.response.send_message(embed=embed, view=DetectionPanel(), ephemeral=True)


# ==============================
# COG
# ==============================

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Register persistent views
        bot.add_view(MainPanel())
        bot.add_view(AIPanel())
        bot.add_view(ModerationPanel())
        bot.add_view(SecurityPanel())
        bot.add_view(DetectionPanel())


    # -------- SETUP --------
    @app_commands.command(name="setup", description="Set moderation log channel")
    async def setup(self, interaction: discord.Interaction, channel: discord.TextChannel):

        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Administrator only.", ephemeral=True)
            return

        await set_log_channel(interaction.guild.id, channel.id)

        await interaction.response.send_message(
            f"Log channel set to {channel.mention}",
            ephemeral=True
        )


    # -------- PANEL --------
    @app_commands.command(name="panel", description="Open main control panel")
    async def panel(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="Main Control Panel",
            description="Select a system panel below.",
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(embed=embed, view=MainPanel())


async def setup(bot):
    await bot.add_cog(Moderation(bot))
