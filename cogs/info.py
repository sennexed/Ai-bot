import discord
from discord.ext import commands
from discord import app_commands
from core.database import get_user_cases, get_reputation, get_top_risk

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="cases", description="View user's last 10 cases")
    async def cases(self, interaction: discord.Interaction, user: discord.Member):
        cases = await get_user_cases(interaction.guild.id, user.id)

        if not cases:
            await interaction.response.send_message("No cases found.", ephemeral=True)
            return

        embed = discord.Embed(title=f"Cases for {user}")
        for case in cases:
            embed.add_field(
                name=f"{case['action']} | Severity {case['severity']}",
                value=case["explanation"],
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="risk", description="Check user risk level")
    async def risk(self, interaction: discord.Interaction, user: discord.Member):
        score = await get_reputation(interaction.guild.id, user.id)
        await interaction.response.send_message(
            f"{user.mention} Reputation Score: {score}",
            ephemeral=True
        )

    @app_commands.command(name="analytics", description="View server risk analytics")
    async def analytics(self, interaction: discord.Interaction):
        top = await get_top_risk(interaction.guild.id)

        embed = discord.Embed(title="Top Risk Users")

        for entry in top:
            member = interaction.guild.get_member(entry["user_id"])
            if member:
                embed.add_field(
                    name=member.name,
                    value=f"Score: {entry['score']}",
                    inline=False
                )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))
