import discord
from discord.ext import commands
from discord import app_commands
from core.database import (
    set_log_channel,
    toggle_ai,
    set_strictness,
    add_infraction
)

# ===========================
# MODERATION PANEL
# ===========================

class ModerationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Warn", style=discord.ButtonStyle.primary, custom_id="mod_warn")
    async def warn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("No permission.", ephemeral=True)
            return
        await interaction.response.send_modal(WarnModal())

    @discord.ui.button(label="Kick", style=discord.ButtonStyle.secondary, custom_id="mod_kick")
    async def kick(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message("No permission.", ephemeral=True)
            return
        await interaction.response.send_modal(KickModal())

    @discord.ui.button(label="Ban", style=discord.ButtonStyle.danger, custom_id="mod_ban")
    async def ban(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("No permission.", ephemeral=True)
            return
        await interaction.response.send_modal(BanModal())


# ===========================
# MODALS
# ===========================

class WarnModal(discord.ui.Modal, title="Warn User"):
    user_id = discord.ui.TextInput(label="User ID")
    reason = discord.ui.TextInput(label="Reason")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            member = await interaction.guild.fetch_member(int(self.user_id.value))

            await add_infraction(
                interaction.guild.id,
                member.id,
                interaction.user.id,
                "WARN",
                self.reason.value
            )

            try:
                await member.send(
                    f"You were warned in {interaction.guild.name}: {self.reason.value}"
                )
            except:
                pass

            await interaction.response.send_message("User warned successfully.", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message("Failed to warn user.", ephemeral=True)


class KickModal(discord.ui.Modal, title="Kick User"):
    user_id = discord.ui.TextInput(label="User ID")
    reason = discord.ui.TextInput(label="Reason")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            member = await interaction.guild.fetch_member(int(self.user_id.value))

            await add_infraction(
                interaction.guild.id,
                member.id,
                interaction.user.id,
                "KICK",
                self.reason.value
            )

            await member.kick(reason=self.reason.value)

            await interaction.response.send_message("User kicked successfully.", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message("Failed to kick user.", ephemeral=True)


class BanModal(discord.ui.Modal, title="Ban User"):
    user_id = discord.ui.TextInput(label="User ID")
    reason = discord.ui.TextInput(label="Reason")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            member = await interaction.guild.fetch_member(int(self.user_id.value))

            await add_infraction(
                interaction.guild.id,
                member.id,
                interaction.user.id,
                "BAN",
                self.reason.value
            )

            await member.ban(reason=self.reason.value)

            await interaction.response.send_message("User banned successfully.", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message("Failed to ban user.", ephemeral=True)


# ===========================
# AI PANEL
# ===========================

class AIView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Toggle AI", style=discord.ButtonStyle.success, custom_id="ai_toggle")
    async def toggle_ai_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Admin only.", ephemeral=True)
            return

        state = await toggle_ai(interaction.guild.id)
        await interaction.response.send_message(f"AI Enabled: {state}", ephemeral=True)

    @discord.ui.button(label="Set Strictness", style=discord.ButtonStyle.primary, custom_id="ai_strict")
    async def strict_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Admin only.", ephemeral=True)
            return
        await interaction.response.send_modal(StrictnessModal())


class StrictnessModal(discord.ui.Modal, title="Set AI Strictness (1-5)"):
    level = discord.ui.TextInput(label="Level")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            value = int(self.level.value)
            if value < 1 or value > 5:
                raise ValueError

            await set_strictness(interaction.guild.id, value)
            await interaction.response.send_message("Strictness updated.", ephemeral=True)

        except:
            await interaction.response.send_message("Invalid number (1-5).", ephemeral=True)


# ===========================
# COG
# ===========================

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(ModerationView())
        bot.add_view(AIView())

    # ---------------- SETUP ----------------

    @app_commands.command(name="setup", description="Set log channel")
    async def setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Admin only.", ephemeral=True)
            return

        await set_log_channel(interaction.guild.id, channel.id)
        await interaction.response.send_message("Log channel set successfully.", ephemeral=True)

    # ---------------- AI PANEL ----------------

    @app_commands.command(name="ai", description="Open AI control panel")
    async def ai(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="AI Moderation Panel",
            description="Control AI settings below.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, view=AIView())

    # ---------------- MODERATION PANEL ----------------

    @app_commands.command(name="moderation", description="Open moderation panel")
    async def moderation(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Moderation Panel",
            description="Manual moderation tools.",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed, view=ModerationView())


async def setup(bot):
    await bot.add_cog(Moderation(bot))
