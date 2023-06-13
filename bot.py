"""Handles all lower level functionality of the discord bot, primarily events and loops"""

import discord
from discord.ext import tasks
from datetime import datetime, time

import config
import gatito as gt


def run_discord_bot():
    TOKEN = config.TOKEN

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = discord.Client(intents=intents)

    gatito = gt.Gatito("stats.json")

    @client.event
    async def on_ready():
        update_status.start()
        update_stats.start()
        update_age.start()

        send_status_update.start()
        print(f"{client.user} is now running!")

        await client.change_presence(status=discord.Status.idle, activity=discord.Game(name=gatito.get_mood()))

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        print(f"{message.author} said: {message.content}")

        old_gatito_mood = gatito.get_mood()
        await gatito.process(message)

        if gatito.get_mood() != old_gatito_mood:
            status = discord.Status.online
            if gatito.state == gt.States.SLEEPING:
                status = discord.Status.idle
            if gatito.state == gt.States.DEAD:
                status = discord.Status.dnd
            await client.change_presence(status=status, activity=discord.Game(name=gatito.get_mood()))


    # FIXME: Maybe scrap this method?
    @tasks.loop(minutes=1)
    async def update_status():
        if client.user.name != "Gatito " + str(gatito.stats["number"]) if gatito.stats["number"] > 1 else "":
            await client.user.edit(username="Gatito " + str(gatito.stats["number"]) if gatito.stats["number"] > 1 else "")

    @tasks.loop(minutes=15)
    async def update_stats():
        gatito.update_stats()
        gatito.save()

    @tasks.loop(hours=24)
    async def update_age():
        gatito.add_age(1)

    @tasks.loop(minutes=1)
    async def send_status_update():
        now = datetime.now().time()
        AM = datetime.now().strftime("%p") == "AM"
        PM = datetime.now().strftime("%p") == "PM"

        if (now == time(8, 00) and AM) or (now == time(9, 45) and PM):
            await gt.messaging.send_message(gatito.respond("!status")[0],
                                            [client.get_channel(int(1112954436076179576))])

    client.run(TOKEN)
