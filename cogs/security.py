import discord
from discord.ext import commands
from discord import app_commands
from core.database import toggle_setting, get_guild_settings, add_infraction, get_log_channel
from utils.raid_detector import record_join, check_raid, record_message, check_spam, excessive_mentions

class SecurityPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Toggle Raid Mode", style=discord.ButtonStyle.danger, custom_id="raid_toggle")
    async def raid(self, interaction: discord.Interaction, button: discord.ui.Button):
        state = await toggle_setting(interaction.guild.id, "raid_mode")
        await interaction.response.send_message(f"Raid Mode: {state}", ephemeral=True)

    @discord.ui.button(label="Toggle Lockdown", style=discord.ButtonStyle.secondary, custom_id="lockdown_toggle")
    async def lockdown(self, interaction: discord.Interaction, button: discord.ui.Button):
        state = await toggle_setting(interaction.guild.id, "lockdown")
        await interaction.response.send_message(f"Lockdown: {state}", ephemeral=True)

    @discord.ui.button(label="Toggle Anti-Spam", style=discord.ButtonStyle.primary, custom_id="spam_toggle")
    async def spam(self, interaction: discord.Interaction, button: discord.ui.Button):
        state = await toggle_setting(interaction.guild.id, "antispam")
        await interaction.response.send_message(f"Anti-Spam: {state}", ephemeral=True)

    @discord.ui.button(label="Toggle Anti-Link", style=discord.ButtonStyle.primary, custom_id="link_toggle")
    async def link(self, interaction: discord.Interaction, button: discord.ui.Button):
        state = await toggle_setting(interaction.guild.id, "antilink")
        await interaction.response.send_message(f"Anti-Link: {state}", ephemeral=True)

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(SecurityPanel())

    @commands.Cog.listener()
    async def on_member_join(self, member):
        record_join(member.guild.id)

        settings = await get_guild_settings(member.guild.id)
        if settings and settings["raid_mode"]:

            if check_raid(member.guild.id):
                for channel in member.guild.text_channels:
                    await channel.set_permissions(member.guild.default_role, send_messages=False)

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        settings = await get_guild_settings(message.guild.id)
        if not settings:
            return

        record_message(message.author.id)

        # Spam detection
        if settings["antispam"] and check_spam(message.author.id):
            await message.delete()
            await message.author.timeout(discord.utils.utcnow() + discord.timedelta(minutes=5))
            await add_infraction(
                message.guild.id,
                message.author.id,
                self.bot.user.id,
                "SPAM",
                "Spam detected",
                50,
                "Automatic spam detection"
            )

        # Mention spam
        if excessive_mentions(message):
            await message.delete()

        # Link detection
        if settings["antilink"] and "http" in message.content.lower():
            await message.delete()

    @app_commands.command(name="security", description="Open security panel")
    async def security(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=discord.Embed(title="Security Panel"),
            view=SecurityPanel()
        )

async def setup(bot):
    await bot.add_cog
cat << 'EOF' > cogs/security.py
import discord
from discord.ext import commands
from discord import app_commands
from core.database import toggle_setting, get_guild_settings, add_infraction, get_log_channel
from utils.raid_detector import record_join, check_raid, record_message, check_spam, excessive_mentions

class SecurityPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Toggle Raid Mode", style=discord.ButtonStyle.danger, custom_id="raid_toggle")
    async def raid(self, interaction: discord.Interaction, button: discord.ui.Button):
        state = await toggle_setting(interaction.guild.id, "raid_mode")
        await interaction.response.send_message(f"Raid Mode: {state}", ephemeral=True)

    @discord.ui.button(label="Toggle Lockdown", style=discord.ButtonStyle.secondary, custom_id="lockdown_toggle")
    async def lockdown(self, interaction: discord.Interaction, button: discord.ui.Button):
        state = await toggle_setting(interaction.guild.id, "lockdown")
        await interaction.response.send_message(f"Lockdown: {state}", ephemeral=True)

    @discord.ui.button(label="Toggle Anti-Spam", style=discord.ButtonStyle.primary, custom_id="spam_toggle")
    async def spam(self, interaction: discord.Interaction, button: discord.ui.Button):
        state = await toggle_setting(interaction.guild.id, "antispam")
        await interaction.response.send_message(f"Anti-Spam: {state}", ephemeral=True)

    @discord.ui.button(label="Toggle Anti-Link", style=discord.ButtonStyle.primary, custom_id="link_toggle")
    async def link(self, interaction: discord.Interaction, button: discord.ui.Button):
        state = await toggle_setting(interaction.guild.id, "antilink")
        await interaction.response.send_message(f"Anti-Link: {state}", ephemeral=True)

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(SecurityPanel())

    @commands.Cog.listener()
    async def on_member_join(self, member):
        record_join(member.guild.id)

        settings = await get_guild_settings(member.guild.id)
        if settings and settings["raid_mode"]:

            if check_raid(member.guild.id):
                for channel in member.guild.text_channels:
                    await channel.set_permissions(member.guild.default_role, send_messages=False)

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        settings = await get_guild_settings(message.guild.id)
        if not settings:
            return

        record_message(message.author.id)

        # Spam detection
        if settings["antispam"] and check_spam(message.author.id):
            await message.delete()
            await message.author.timeout(discord.utils.utcnow() + discord.timedelta(minutes=5))
            await add_infraction(
                message.guild.id,
                message.author.id,
                self.bot.user.id,
                "SPAM",
                "Spam detected",
                50,
                "Automatic spam detection"
            )

        # Mention spam
        if excessive_mentions(message):
            await message.delete()

        # Link detection
        if settings["antilink"] and "http" in message.content.lower():
            await message.delete()

    @app_commands.command(name="security", description="Open security panel")
    async def security(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=discord.Embed(title="Security Panel"),
            view=SecurityPanel()
        )

async def setup(bot):
    await bot.add_cog
(security(bot))
