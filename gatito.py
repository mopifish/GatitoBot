""" Module for Gatito Class"""

# TODO: Gatito takes damage from empty stats
# TODO: Let gatito die
# TODO: Rebalance stat loss
# --- JSON Work ---
# TODO: Save stats
# TODO: Redo the food list
# --- COMMANDS ---
# TODO: Pet Command
# TODO: Wakeup command (send someone messages till they respond)
# TODO: Announce command

import discord
import emoji
from enum import Enum
import json
import math

import messaging
import icecream as debug

COMMAND_SYMBOL = "!"
COMMANDS = {
    "wakeup": ["!goodmorning", "!wakeup", "!morning"],
    "spit": ["!spit", "!ptoeey"],
    "punch": ["!punch"],
    "slap": ["!slap"],
    "kiss": ["!kiss"],
    "sleep": ["!goodnight", "!sleep", "!night"],
    "eat": ["!eat"],
    "status": ["!status"]

}


def get_all_commands():
    commands_list = []
    for k, v in COMMANDS.items():
        for item in v:
            commands_list.append(item)

    return commands_list


class Status(Enum):
    GOOD = 1
    OKAY = 2
    BAD = 3
    SLEEPING = 4


class Gatito:
    def __init__(self, number):
        with open("stats.json") as f:
            self.stats = json.load(f)

        # Gatito Initialization
        self._number = number
        self._age = 1

        self.mood = "Okay"
        self.status = Status.GOOD

        self.max_health = 100
        self.health = self.max_health
        self.max_hunger = 100
        self.hunger = self.max_hunger
        self.max_sleep = 100
        self.sleep = self.max_sleep

        self.sleeping = True

        self.previous_target = None

    async def process(self, message):
        targets = messaging.get_all_targets(message)
        responses, actions = self.respond(message.content)

        await messaging.send_message(responses, targets)

        self.previous_target = targets
        for pair in actions:
            pair[0](pair[1])

    def respond(self, message):
        if COMMAND_SYMBOL not in message:
            return [], []

        command = message[message.find(COMMAND_SYMBOL):].lower().split()

        responses = []
        actions = []

        # --- Stateless Commands ---
        if command[0] in COMMANDS["status"]:
            embed = self.get_status_embed()
            responses.append(embed)

        # --- Sleeping Commands ---
        elif self.sleeping:
            if command[0] in COMMANDS["wakeup"]:
                responses.append("media/wakeup.gif")
                actions.append((self.set_sleeping, False))
            elif command[0] in get_all_commands():
                responses = ["mimimimmemimim 💤💤(shh! he's sleeping!)"]

        # --- Awake Commands ---
        else:
            if command[0] in COMMANDS["wakeup"]:
                responses.append("ai'm!! Awaek!!!")

            elif command[0] in COMMANDS["spit"]:
                responses.append("💦💦💦")

            elif command[0] in COMMANDS["punch"]:
                responses.append("👊💥💥")

            elif command[0] in COMMANDS["slap"]:
                responses.append("🫲💥💥")

            elif command[0] in COMMANDS["kiss"]:
                responses.append("media/cat-kiss-kiss-cat.gif")

            elif command[0] in COMMANDS["sleep"]:
                responses.append("media/yawn.gif")
                actions.append((self.set_sleeping, True))

            elif command[0] in COMMANDS["eat"] and len(command) > 1:

                for food in command[1:]:
                    if food in self.stats["BEST_FOODS"]:
                        responses.append("Sloorp mm Glorrp SLurp!! I love " + food)
                        actions.append((self.add_hunger, 5))
                    elif food in self.stats["GOOD_FOODS"]:
                        responses.append("Armf Narmf Narmf! Mmm " + food)
                        actions.append((self.add_hunger, 3))
                    elif food in self.stats["BAD_FOODS"]:
                        actions.append((self.add_hunger, 1))
                        responses.append("Steenky!! I hate " + food)
                    elif food in self.stats["POISONOUS_FOODS"]:
                        responses.append("HYYYEUUUUUCKKKKK PPEEYEYPPEYEEWWW! 👎👎 " + food + "❗❗")
                        actions.append((self.add_health, -1))
                    else:
                        responses.append("OUCHYYY I can NAWT eet THEIS!❗❗")
                        actions.append((self.add_health, -1))

        return responses, actions

    # ------------------------------------ UPDATE METHODS ------------------------------------
    def update_mood(self):
        self.mood = "Good"
        self.status = Status.GOOD

        if self.hunger < 50:
            self.mood = "Hungry"
            self.status = Status.OKAY

        if self.hunger < 20:
            self.mood = "Starving"
            self.status = Status.BAD

        if self.sleeping:
            self.mood = "Eeping 💤💤"
            self.status = Status.SLEEPING

    # ------------------------------------ GET METHODS ------------------------------------
    def get_status_embed(self):
        embed = discord.Embed(title="🌟GATITO STATUS🌟", description="Feeling: " + "mood", color=0x00ff00)
        embed.add_field(name="HEALTH" + str(self.health) + "/" + str(self.max_health),
                        value=emoji.emojize(":heart:") * math.ceil(self.health / 10) + emoji.emojize(":broken_heart:") * math.ceil((self.max_health - self.health) / 10), inline=False)
        embed.add_field(name="HUNGER: " + str(self.hunger) + "/" + str(self.max_hunger),
                        value="🟩" * math.ceil(self.hunger / 10) + "🟥" * math.ceil((self.max_hunger - self.hunger) / 10), inline=False)
        embed.add_field(name="SLEEP: " + str(self.sleep) + "/" + str(self.max_sleep),
                        value="🟩" * math.ceil(self.sleep / 10) + "🟥" * math.ceil((self.max_sleep - self.sleep) / 10), inline=False)
        return embed

    # ------------------------------------ SETTERS ------------------------------------
    def add_health(self, value):
        self.health += value
        self.health = max(min(self.health, self.max_health), 0)

    def add_hunger(self, value):
        self.hunger += value
        self.hunger = max(min(self.hunger, self.max_hunger), 0)

    def add_sleep(self, value):
        self.sleep += value
        self.sleep = max(min(self.sleep, self.max_sleep), 0)

    def set_sleeping(self, value):
        self.sleeping = value

