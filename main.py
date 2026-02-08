import discord
from discord.ext import commands, tasks
import os
import requests
from dotenv import load_dotenv
import datetime

# 1. Load Environment Variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
# We use a fallback empty string to avoid errors during local testing
CHANNEL_ID = os.getenv("CHANNEL_ID")

# 2. Setup Bot Intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 3. DAILY FEATURE (Fixed for GitHub Actions)
# Since the bot restarts every 5 hours, we check the clock every hour instead.
@tasks.loop(minutes=60)
async def daily_deals():
    now = datetime.datetime.utcnow()
    # This will only trigger during the 12:00 UTC hour
    if now.hour == 12:
        channel = bot.get_channel(int(CHANNEL_ID))
        if channel:
            url = "https://www.cheapshark.com/api/1.1/deals?storeID=1&upperPrice=5&pageSize=5"
            try:
                response = requests.get(url).json()
                if response:
                    msg = "**🎯 Daily Steam Deals (Under $5):**\n"
                    for deal in response:
                        msg += f"- {deal['title']}: **${deal['salePrice']}** (~~${deal['normalPrice']}~~)\n<https://www.cheapshark.com/redirect?dealID={deal['dealID']}>\n"
                    await channel.send(msg)
            except Exception as e:
                print(f"Error fetching deals: {e}")

# 4. MANUAL COMMANDS
@bot.command()
async def deal(ctx, *, game: str):
    """Search for a specific game: !deal [name]"""
    url = f"https://www.cheapshark.com/api/1.1/deals?title={game}&limit=1"
    data = requests.get(url).json()
    
    if data:
        d = data[0]
        # Using an 'Embed' link format <link> hides the big ugly preview
        await ctx.send(f"✅ **{d['title']}** is currently **${d['salePrice']}**!\nLink: <https://www.cheapshark.com/redirect?dealID={d['dealID']}>")
    else:
        await ctx.send(f"❌ No deals found for '{game}'.")

@bot.command()
async def ping(ctx):
    """Test if the bot is alive"""
    await ctx.send(f"🏓 Pong! Latency: {round(bot.latency * 1000)}ms")

# 5. BOT STARTUP
@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")
    # Start the background task
    if not daily_deals.is_running():
        daily_deals.start()

# Start the bot
if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("ERROR: No DISCORD_TOKEN found. Check your GitHub Secrets or .env file.")