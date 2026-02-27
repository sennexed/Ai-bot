import discord
from discord.ext import commands
from discord import app_commands
from core.database import (
    get_user_cases,
    get_reputation,
    get_case,
    create_appeal
)

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="case", description="View specific case")
    async def case(self, interaction: discord.Interaction, case_id: int):
        case = await get_case(case_id)

        if not case:
            await interaction.response.send_message("Case not found.", ephemeral=True)
            return

        embed = discord.Embed(title=f"Case #{case_id}")
        embed.add_field(name="Action", value=case["action"])
        embed.add_field(name="Severity", value=case["severity"])
        embed.add_field(name="Reason", value=case["explanation"], inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="appeal", description="Appeal a case")
    async def appeal(self, interaction: discord.Interaction, case_id: int, reason: str):
        await create_appeal(
            interaction.guild.id,
            case_id,
            interaction.user.id,
            reason
        )

        await interaction.response.send_message(
            "Appeal submitted to moderators.",
            ephemeral=True
        )

    @app_commands.command(name="risk", description="Check user risk level")
    async def risk(self, interaction: discord.Interaction, user: discord.Member):
        score = await get_reputation(interaction.guild.id, user.id)
        await interaction.response.send_message(
            f"{user.mention} Reputation Score: {score}",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Info(bot))
