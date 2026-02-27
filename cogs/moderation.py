import discord
from discord.ext import commands
from discord import app_commands
from core.database import (
    set_log_channel,
    get_log_channel,
    add_infraction
)

# ================= MAIN PANEL =================

class MainPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Moderation", style=discord.ButtonStyle.primary, custom_id="panel_mod")
    async def mod(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            embed=discord.Embed(title="Moderation Panel"),
            view=ModerationPanel(),
            ephemeral=True
        )


# ================= MOD PANEL =================

class ModerationPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Warn", style=discord.ButtonStyle.secondary, custom_id="warn_btn")
    async def warn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(WarnModal())

    @discord.ui.button(label="Kick", style=discord.ButtonStyle.secondary, custom_id="kick_btn")
    async def kick(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(KickModal())

    @discord.ui.button(label="Ban", style=discord.ButtonStyle.danger, custom_id="ban_btn")
    async def ban(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BanModal())


# ================= MODALS =================

class WarnModal(discord.ui.Modal, title="Warn User"):
    user = discord.ui.TextInput(label="User ID")
    reason = discord.ui.TextInput(label="Reason")

    async def on_submit(self, interaction: discord.Interaction):
        member = await interaction.guild.fetch_member(int(self.user.value))
        await add_infraction(
            interaction.guild.id,
            member.id,
            interaction.user.id,
            "WARN",
            self.reason.value,
            0,
            self.reason.value
        )

        try:
            await member.send(f"You were warned: {self.reason.value}")
        except:
            pass

        log_channel_id = await get_log_channel(interaction.guild.id)
        if log_channel_id:
            channel = interaction.guild.get_channel(log_channel_id)
            await channel.send(
                embed=discord.Embed(
                    title="User Warned",
                    description=f"{member.mention}\nReason: {self.reason.value}"
                )
            )

        await interaction.response.send_message("Warned successfully.", ephemeral=True)


class KickModal(discord.ui.Modal, title="Kick User"):
    user = discord.ui.TextInput(label="User ID")
    reason = discord.ui.TextInput(label="Reason")

    async def on_submit(self, interaction: discord.Interaction):
        member = await interaction.guild.fetch_member(int(self.user.value))
        await member.kick(reason=self.reason.value)

        await add_infraction(
            interaction.guild.id,
            member.id,
            interaction.user.id,
            "KICK",
            self.reason.value,
            0,
            self.reason.value
        )

        await interaction.response.send_message("Kicked successfully.", ephemeral=True)


class BanModal(discord.ui.Modal, title="Ban User"):
    user = discord.ui.TextInput(label="User ID")
    reason = discord.ui.TextInput(label="Reason")

    async def on_submit(self, interaction: discord.Interaction):
        member = await interaction.guild.fetch_member(int(self.user.value))
        await member.ban(reason=self.reason.value)

        await add_infraction(
            interaction.guild.id,
            member.id,
            interaction.user.id,
            "BAN",
            self.reason.value,
            0,
            self.reason.value
        )

        await interaction.response.send_message("Banned successfully.", ephemeral=True)


# ================= COG =================

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(MainPanel())
        bot.add_view(ModerationPanel())

    @app_commands.command(name="setup", description="Set log channel")
    async def setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Admin only.", ephemeral=True)
            return

        await set_log_channel(interaction.guild.id, channel.id)
        await interaction.response.send_message("Log channel set.", ephemeral=True)

    @app_commands.command(name="panel", description="Open control panel")
    async def panel(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Control Panel")
        await interaction.response.send_message(embed=embed, view=MainPanel())


async def setup(bot):
    await bot.add_cog(Moderation(bot))
