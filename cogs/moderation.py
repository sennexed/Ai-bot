import discord
from discord.ext import commands
from discord import app_commands
from core.database import (
    add_infraction,
    get_user_infractions,
    get_toxicity,
    set_log_channel,
    get_log_channel,
    toggle_ai
)


class ModPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Warn", style=discord.ButtonStyle.primary, custom_id="panel_warn")
    async def warn_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Use /warn command.", ephemeral=True)

    @discord.ui.button(label="Mute", style=discord.ButtonStyle.secondary, custom_id="panel_mute")
    async def mute_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Use /mute command.", ephemeral=True)

    @discord.ui.button(label="Ban", style=discord.ButtonStyle.danger, custom_id="panel_ban")
    async def ban_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Use /ban command.", ephemeral=True)

    @discord.ui.button(label="Infractions", style=discord.ButtonStyle.success, custom_id="panel_infractions")
    async def inf_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Use /infractions command.", ephemeral=True)

    @discord.ui.button(label="Toggle AI", style=discord.ButtonStyle.secondary, custom_id="panel_ai")
    async def ai_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        new_state = await toggle_ai(interaction.guild.id)
        await interaction.response.send_message(f"AI Enabled: {new_state}", ephemeral=True)


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(ModPanel())


    # ---------------- SETUP ----------------
    @app_commands.command(name="setup", description="Setup moderation log channel")
    async def setup(self, interaction: discord.Interaction, channel: discord.TextChannel):

        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Admin only.", ephemeral=True)
            return

        await set_log_channel(interaction.guild.id, channel.id)

        await interaction.response.send_message(
            f"Log channel set to {channel.mention}"
        )


    # ---------------- PANEL ----------------
    @app_commands.command(name="panel", description="Open moderation panel")
    async def panel(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="Moderation Control Panel",
            description="Use buttons below.",
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(embed=embed, view=ModPanel())


    # ---------------- WARN ----------------
    @app_commands.command(name="warn", description="Warn user")
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):

        await add_infraction(
            interaction.guild.id,
            member.id,
            interaction.user.id,
            "warn",
            reason,
            10
        )

        await interaction.response.send_message(f"{member.mention} warned.")


    # ---------------- MUTE ----------------
    @app_commands.command(name="mute", description="Timeout user")
    async def mute(self, interaction: discord.Interaction, member: discord.Member, minutes: int):

        until = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
        await member.timeout(until)

        await interaction.response.send_message(f"{member.mention} muted.")


    # ---------------- BAN ----------------
    @app_commands.command(name="ban", description="Ban user")
    async def ban(self, interaction: discord.Interaction, member: discord.Member):

        await member.ban()

        await interaction.response.send_message(f"{member.mention} banned.")


    # ---------------- INFRACTIONS ----------------
    @app_commands.command(name="infractions", description="View infractions")
    async def infractions(self, interaction: discord.Interaction, member: discord.Member):

        rows = await get_user_infractions(
            interaction.guild.id,
            member.id
        )

        if not rows:
            await interaction.response.send_message("No infractions.")
            return

        text = ""
        for r in rows[:10]:
            text += f"{r['action']} | {r['reason']}\n"

        await interaction.response.send_message(text)


    # ---------------- TOXICITY ----------------
    @app_commands.command(name="toxicity", description="Check toxicity")
    async def toxicity(self, interaction: discord.Interaction, member: discord.Member):

        score = await get_toxicity(interaction.guild.id, member.id)
        await interaction.response.send_message(f"Toxicity: {score}")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
