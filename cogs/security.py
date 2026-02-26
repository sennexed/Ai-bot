import discord
from discord.ext import commands
from utils.raid_detector import detect_raid

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if detect_raid():
            for channel in member.guild.text_channels:
                await channel.edit(slowmode_delay=10)

async def setup(bot):
    await bot.add_cog(Security(bot))
