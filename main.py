import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import datetime

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@tasks.loop(hours=24)
async def daily_deals():
    channel = bot.get_channel(int(os.getenv("CHANNEL_ID")))
    await channel.send("🔍 Checking for today's discounts...")

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    if not daily_deals.is_running():
        daily_deals.start()

bot.run(TOKEN)