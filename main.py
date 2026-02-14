import discord
from discord.ext import commands, tasks
import os
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
URL = "https://www.cheapshark.com/api/1.0/deals"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        content = message.content.replace(f'<@!{bot.user.id}>', '').replace(f'<@{bot.user.id}>', '').strip()
        if content:
            ctx = await bot.get_context(message)
            await deal(ctx, content)
        else:
            await message.channel.send("👋 Mention me with a game name, 'free', or 'under [price]'!")
    else:
        await message.channel.send("I'm so lonelyyyyy, I have nobodyyyyyy 🎶🐌")

async def deal(ctx, cmd: str):
    cmds = cmd.split()
    params = {
        "storeID": "1",
        "pageSize": 3
    }

    try:
        if cmds[0].lower() == "ping":
            return await ctx.send(f"🏓 Pong! Latency: {round(bot.latency * 1000)}ms")
        elif cmds[0].lower() == "under" and len(cmds) > 1:
            params["upperPrice"] = cmds[1]
        elif cmds[0].lower() == "free":
            params["upperPrice"] = 0
        else:
            params["title"] = cmd

        response = requests.get(URL, params=params)
        games = response.json()

        if games:
            for game in games[:3]:
                title = game['title']
                price = game['salePrice']
                s_id = game['steamAppID']
                link = f"https://store.steampowered.com/app/{s_id}/"
                await ctx.send(f"✅ **{title}** is **${price}**!\n<{link}>")
        else:
            await ctx.send("❓ No deals found for that request.")
            
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("⚠️ API error. Check your format.")

if __name__ == "__main__":
    bot.run(TOKEN)