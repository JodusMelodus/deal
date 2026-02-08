import discord
from discord.ext import commands, tasks
import os
import requests
from dotenv import load_dotenv
import datetime

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@tasks.loop(minutes=60)
async def daily_deals():
    now = datetime.datetime.utcnow()

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

@bot.command()
async def deal(ctx, *, game: str):
    """Search for a Steam deal: !deal [name]"""

    url = f"https://www.cheapshark.com/api/1.1/deals?title={game}&storeID=1&limit=1"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data:
            d = data[0]
            title = d['title']
            sale_price = d['salePrice']
            normal_price = d['normalPrice']
            savings = round(float(d['savings']))
            

            steam_id = d['steamAppID']
            steam_url = f"https://store.steampowered.com/app/{steam_id}/"
            
            message = (
                f"✅ **{title}** is on sale!\n"
                f"💰 Price: **${sale_price}** (~~${normal_price}~~) — {savings}% off\n"
                f"🔗 View on Steam: <{steam_url}>"
            )
            await ctx.send(message)
        else:
            await ctx.send(f"❌ No Steam deals found for '{game}'.")
            
    except Exception as e:
        await ctx.send("⚠️ Error reaching the deal database.")
        print(f"API Error: {e}")

@bot.command()
async def ping(ctx):
    """Test if the bot is alive"""
    await ctx.send(f"🏓 Pong! Latency: {round(bot.latency * 1000)}ms")

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

    if not daily_deals.is_running():
        daily_deals.start()

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("ERROR: No DISCORD_TOKEN found. Check your GitHub Secrets or .env file.")