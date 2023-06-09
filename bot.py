"""Handles all lower level functionality of the discord bot, primarily events and loops"""

import discord
from discord.ext import tasks
from datetime import datetime, time
import asyncio
import icecream as debug

import config

import gatito as gt


def run_discord_bot():
    TOKEN = config.TOKEN

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = discord.Client(intents=intents)

    gatito = gt.Gatito(1)

    @client.event
    async def on_ready():
        update_status.start()
        update_stats.start()
        #send_status_update.start()
        print(f"{client.user} is now running!")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        print(f"{message.author} said: {message.content}")

        await gatito.process(message)

    @tasks.loop(minutes=1)
    async def update_status():
        gatito.update_mood()
        status = discord.Status.online

        if gatito.status == gt.Status.SLEEPING:
            status = discord.Status.idle
        elif gatito.status == gt.Status.BAD:
            status = discord.Status.dnd

        await client.change_presence(status=status, activity=discord.Game(name=gatito.mood))

    @tasks.loop(minutes=15)
    async def update_stats():
        gatito.add_hunger(-1)
        gatito.add_sleep(1 if gatito.sleeping else -1)

    # @tasks.loop(minutes=1)
    # async def send_status_update():
    #     now = datetime.now().time()
    #     AM = datetime.now().strftime("%p") == "AM"
    #     PM = datetime.now().strftime("%p") == "PM"
    #
    #     #TODO: Properly set up status printing, once 24 hour hosting
    #
    #     # if (now == time(8, 00) and AM) or (now == time(9, 45) and PM):
    #     #     await gt.messaging.send_message(gatito.respond("!status")[0], [client.get_channel(int(1112954436076179576))])

    client.run(TOKEN)
