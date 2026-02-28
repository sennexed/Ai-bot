import discord
from discord.ext import commands
from discord import app_commands
from utils.ai import analyze_message
from core.database import (
    add_infraction,
    count_user_infractions,
    get_log_channel,
    get_guild_settings,
    log_staff_action,
    pool
)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =========================================
    # AUTO AI MODERATION LISTENER
    # =========================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if not message.guild:
            return

        if message.author.bot:
            return

        # Fetch AI status
        settings = await get_guild_settings(message.guild.id)
        if not settings or not settings["ai_enabled"]:
            return

        result = await analyze_message(message.content)
        if not result:
            return

        severity = int(result.get("severity", 0))
        action = result.get("action", "none")
        confidence = float(result.get("confidence", 0))
        explanation = result.get("explanation", "No explanation")

        if severity < 40:
            return  # Ignore low severity

        # Store infraction
        case_id = await add_infraction(
            message.guild.id,
            message.author.id,
            self.bot.user.id,
            action.upper(),
            explanation,
            severity,
            confidence,
            explanation
        )

        # Count infractions for escalation
        count = await count_user_infractions(
            message.guild.id,
            message.author.id
        )

        # Escalation logic
        try:
            if count >= 5:
                await message.guild.ban(
                    message.author,
                    reason="AI escalation: repeated violations"
                )
                final_action = "BAN"

            elif count >= 3:
                await message.author.timeout(
                    discord.utils.utcnow() + discord.timedelta(minutes=10),
                    reason="AI escalation timeout"
                )
                final_action = "TIMEOUT"

            else:
                await message.delete()
                final_action = "WARN"

        except Exception:
            final_action = "FAILED"

        # Log embed
        log_channel_id = await get_log_channel(message.guild.id)
        if log_channel_id:
            channel = message.guild.get_channel(log_channel_id)
            if channel:
                embed = discord.Embed(
                    title=f"AI Moderation Case #{case_id}",
                    color=discord.Color.red()
                )
                embed.add_field(name="User", value=message.author.mention)
                embed.add_field(name="Severity", value=str(severity))
                embed.add_field(name="Confidence", value=str(confidence))
                embed.add_field(name="Action", value=final_action)
                embed.add_field(name="Explanation", value=explanation, inline=False)
                await channel.send(embed=embed)

    # =========================================
    # MANUAL COMMANDS
    # =========================================

    @app_commands.command(name="warn", description="Warn a user manually")
    async def warn(self, interaction: discord.Interaction,
                   member: discord.Member,
                   reason: str):

        await add_infraction(
            interaction.guild.id,
            member.id,
            interaction.user.id,
            "WARN",
            reason,
            50,
            1.0,
            "Manual moderation"
        )

        await log_staff_action(
            interaction.guild.id,
            interaction.user.id,
            "WARN",
            None
        )

        await interaction.response.send_message(
            f"{member.mention} has been warned."
        )

    @app_commands.command(name="cases", description="View user cases")
    async def cases(self, interaction: discord.Interaction,
                    member: discord.Member):

        from core.database import get_user_cases
        records = await get_user_cases(
            interaction.guild.id,
            member.id
        )

        if not records:
            return await interaction.response.send_message(
                "No cases found."
            )

        embed = discord.Embed(
            title=f"Cases for {member}",
            color=discord.Color.orange()
        )

        for r in records[:5]:
            embed.add_field(
                name=f"Case #{r['id']} - {r['action']}",
                value=r["reason"],
                inline=False
            )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
