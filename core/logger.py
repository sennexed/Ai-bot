import discord
import json

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

async def log_action(bot, guild, title, description):
    config = load_config()
    channel_id = config.get("log_channel")

    if not channel_id:
        return

    channel = guild.get_channel(channel_id)
    if not channel:
        return

    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.red()
    )
    await channel.send(embed=embed)
