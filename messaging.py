import discord
import os
import asyncio


def get_all_targets(message):
    targets = []

    if len(message.mentions) > 0:
        targets += message.mentions
    if len(message.role_mentions) > 0:
        targets += sum([role.members for role in message.role_mentions], [])

    if len(targets) == 0:
        targets += [message.channel]

    return targets


async def send_message(responses, targets):
    try:
        for target in targets:
            for response in responses:
                if isinstance(response, discord.Embed):
                    await target.send(embed=response)
                elif os.path.isfile(response):
                    await target.send(file=discord.File(response))
                else:
                    await target.send(response)

                await asyncio.sleep(1)
    except Exception as e:
        print("Exception: " + str(e))
