import discord
import json
from discord.ext import commands

with open('config.json') as config_file:
    config = json.load(config_file)
discord_stuff = config.get('discord', {})
token = discord_stuff.get('token')
channel_id = discord_stuff.get('channel_id')
enabled = discord_stuff.get('enabled')

if enabled:
    client = commands.Bot(command_prefix="!", intents=discord.Intents.default())
    async def message_send(message):
        if not channel:
            return
        await channel.send(message)
    
    @client.event
    async def on_ready():
        print(f'Logged in as {client.user} (ID: {client.user.id})')
        print('------')
        global channel
        channel = await client.fetch_channel(channel_id)
        await channel.send("Bot is ready!")
        print(f"channel id: {channel_id}")
        print(f"channel object: {channel}")

    def start_bot():
        client.run(token)
        