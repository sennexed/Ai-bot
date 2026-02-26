import discord
from discord.ext import commands
from discord import app_commands

class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="purge")
    async def purge(self, interaction: discord.Interaction, amount: int):
        await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(
            f"Deleted {amount} messages.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Management(bot))
