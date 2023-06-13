""" Module for Gatito Class"""

# PLAY UPDATE: V 1.1.0
# TO/DO: Add more moods
# TO/DO: Add play/happiness meter
# TO/DO: Add games

# RELEASE: V 1.0.0
# TODO: Consider mapping function calls to possible dict responses?
# TODO: Tidy up bot.py, and consider chaning the bot.py > gatito hierarchy
# TODO: shrink gifs
# FIXME: actions like !sleep dont update state until after the gif has sent. Consider removing actions list and decoupling these two events
# --- COMMANDS ---
# - Wakeup command (send someone messages till they respond)
# - Announce command
# - Drink command?
# - Dressup command?

import discord
from enum import Enum
import json
import random

import messaging
import icecream as debug

# The following have potential for their own class or file
COMMAND_SYMBOL = "!"
COMMANDS = {
    "wakeup": ["!goodmorning", "!wakeup", "!morning", "!wake"],
    "spit": ["!spit", "!ptoeey"],
    "punch": ["!punch"],
    "slap": ["!slap"],
    "kiss": ["!kiss"],
    "dance": ["!dance", "!play", "!jump", "!yippee", "!happy"],
    "pet": ["!pet", "!scritch"],
    "sniff": ["!sniff", "!jeffthekiller"],

    "sleep": ["!goodnight", "!sleep", "!night"],
    "bestfoods": ["!bestfoods", "!favorites", "!lovedfoods", "!yummys", "!yummies"],
    "goodfoods": ["!goodfoods", "!likes", "!goods", "!likedfoods"],
    "badfoods": ["!badfoods", "!bads", "!hates", "!hatedfoods"],
    "poisonfoods": ["!poisonousfoods", "!poison", "!poisons", "!dangerfoods", "!poisonfoods"],
    "eat": ["!eat"],
    "drink": ["!drink", "!slurp"],
    "status": ["!status"],
    "resurrect": ["!resurrect", "!live", "!rise", "!revive"]

}
def get_all_commands():
    commands_list = []
    for k, v in COMMANDS.items():
        for item in v:
            commands_list.append(item)

    return commands_list

RESPONSES = {
    "wakeup": ["ai'm!! Awaek!!!", "ghuhgh!! Hugh!GH!!", "stopp EIT!!!!"],
    "spit": ["💦💦💦"],
    "punch": ["👊💥💥"],
    "slap": ["🫲💥💥"],
    "kiss": ["media/kiss.gif"],
    "dance": ["media/dance.gif"],
    "pet": ["media/normal_pet.gif", "media/fast_pet.gif", "media/slow_pet.gif", "media/squishy_pet.gif"],
    "sniff": ["media/sniff.gif"],

    "dead": ["media/dead.gif", "media/dead2.gif", "media/dead3.gif", "media/dead4.gif"],
}

class States(Enum):
    AWAKE = 1,
    SLEEPING = 2,
    DEAD = 3

class Gatito:
    def __init__(self, stats_path, number=None):
        try:
            # Attempts to load stats.json
            with open(stats_path) as f:
                self.stats = json.load(f)
        except FileNotFoundError:
            # If no stats are found (indicating fresh copy) new stats are created
            with open("stats.default.json") as f:
                self.stats = json.load(f)
            self.save()

        if number is not None: self.stats["number"] = number
        self.state = States.SLEEPING

        self.previous_target = None



    def save(self):
        with open("stats.json", "w") as f:
            json.dump(self.stats, f)

    async def process(self, message):
        targets = messaging.get_all_targets(message)
        responses, actions = self.respond(message.content)

        await messaging.send_message(responses, targets)

        self.previous_target = targets
        for pair in actions:
            try:
                pair[0](pair[1])
            except TypeError:
                pair()

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

        elif self.state == States.DEAD:
            # Responds with a random "dead" gif if any command is called
            if command[0] in COMMANDS["wakeup"]:
                responses.append(random.choice(RESPONSES["dead"]))
            elif command[0] in COMMANDS["resurrect"]:
                responses.append("🪄✨💖✨💖")
                responses.append("💢GROOUUAHHHHHHH💢")
                actions.append(self.resurrect)
            elif command[0] in get_all_commands():
                responses = ["mimimimmemimim 💤💤(shh! he's sleeping!)"]

        elif self.state == States.SLEEPING:
            if command[0] in COMMANDS["wakeup"]:
                responses.append("media/wakeup.gif")
                actions.append((self.set_state, States.AWAKE))
            elif command[0] in get_all_commands():
                responses = ["mimimimmemimim 💤💤(shh! he's sleeping!)"]

        elif self.state == States.AWAKE:
            # Handles all genertic text responses
            for k, v in COMMANDS.items():
                if command[0] in v and k in RESPONSES:
                    responses.append(random.choice(RESPONSES[k]))

            # More complex and action commands
            if command[0] in COMMANDS["sleep"]:
                responses.append("media/yawn.gif")
                actions.append((self.set_state, States.SLEEPING))

            elif command[0] in COMMANDS["bestfoods"]:
                responses.append(("I love love love theese! " + "".join(self.stats["known_best_foods"])) if len(
                    self.stats["known_best_foods"]) else "I don lolove anyfing........")
            elif command[0] in COMMANDS["goodfoods"]:
                responses.append(("I like theese! " + "".join(self.stats["known_good_foods"])) if len(
                    self.stats["known_good_foods"]) else "I don likke anyfing........")
            elif command[0] in COMMANDS["badfoods"]:
                responses.append(("Thees arr GROSS!!! " + "".join(self.stats["known_bad_foods"])) if len(
                    self.stats["known_bad_foods"]) else "I like everyfing!! Nuffins yuckyee")
            elif command[0] in COMMANDS["poisonfoods"]:
                responses.append(("Thees HURTTT!!!!!! " + "".join(self.stats["known_poisonous_foods"])) if len(
                    self.stats["known_poisonous_foods"]) else "Ai'm Invincble, nuffin hurts me!!")

            elif command[0] in COMMANDS["eat"] and len(command) > 1:
                for food in command[1:]:
                    if food in self.stats["BEST_FOODS"]:
                        responses.append("Sloorp mm Glorrp SLurp!! I love " + food)
                        actions.append((self.add_hunger, 15))

                        # Discovers food if it is undiscovered
                        if food not in self.stats["known_best_foods"]: self.stats["known_best_foods"].append(food)
                    elif food in self.stats["GOOD_FOODS"]:
                        responses.append("Armf Narmf Narmf! Mmm " + food)
                        actions.append((self.add_hunger, 10))

                        # Discovers food if it is undiscovered
                        if food not in self.stats["known_good_foods"]: self.stats["known_good_foods"].append(food)
                    elif food in self.stats["BAD_FOODS"]:
                        actions.append((self.add_hunger, 10))
                        responses.append("Steenky!! I hate " + food)

                        # Discovers food if it is undiscovered
                        if food not in self.stats["known_bad_foods"]: self.stats["known_bad_foods"].append(food)
                    elif food in self.stats["POISONOUS_FOODS"]:
                        responses.append("HYYYEUUUUUCKKKKK PPEEYEYPPEYEEWWW! 👎👎 " + food + "❗❗")
                        actions.append((self.add_health, -5))

                        # Discovers food if it is undiscovered
                        if food not in self.stats["known_poisonous_foods"]: self.stats["known_poisonous_foods"].append(
                            food)
                    else:
                        responses.append("OUCHYYY I can NAWT eet THEIS!❗❗")
                        actions.append((self.add_health, -1))
                    # elif command[0] in COMMANDS["drink"] and len(command) > 1:
                    #     responses.append("Glug glug gloogl glugl")
                    #     for drink in command[1:]:
                    #         if drink == emoji.emojize(":milk:"):
                    #             responses.append("PFP:media/gatito.png")
                    #         elif drink == emoji.emojize(":beer:"):
                    #             responses.append("PFP:media/clonetito.png")

        return responses, actions

    # ------------------------------------ UPDATE METHODS ------------------------------------
    def get_mood(self):
        mood = "Good"

        if self.state == States.AWAKE:
            if self.stats["hunger"] < 50:
                mood = "Hungry"
            if self.stats["hunger"] < 20:
                mood = "Starving"

        elif self.state == States.SLEEPING:
            mood = "Eeping 💤💤"
        elif self.state == States.DEAD:
            mood = "☠️🦴DEAD💀🦴"

        return mood

    def update_stats(self):
        self.add_hunger(-2)
        self.add_sleep(2 if self.state == States.SLEEPING else -2)

        if self.stats["hunger"] <= 0:
            self.add_health(-5)
        elif self.stats["hunger"] >= 0.9 * self.stats["MAX_HUNGER"]:
            self.add_health(5)
        if self.stats["sleep"] <= 0:
            self.add_health(-5)
        if self.stats["sleep"] >= 0.9 * self.stats["MAX_SLEEP"]:
            self.add_health(5)

    def resurrect(self):
        self.__init__("stats.default.json", self.stats["number"] + 1)

    # ------------------------------------ GET METHODS ------------------------------------
    def get_status_embed(self):
        embed = discord.Embed(title="🌟GATITO STATUS🌟",
                              description="Feeling: " + self.get_mood() + "\nAge: " + str(self.stats["age"]) + " days",
                              color=0x00ff00)
        embed.add_field(name="HEALTH: " + str(self.stats["health"]) + "/" + str(self.stats["MAX_HEALTH"]),
                        value="❤️" * round(self.stats["health"] / 10) + "💔" * round(
                            (self.stats["MAX_HEALTH"] - self.stats["health"]) / 10), inline=False)
        embed.add_field(name="HUNGER: " + str(self.stats["hunger"]) + "/" + str(self.stats["MAX_HUNGER"]),
                        value="🟩" * round(self.stats["hunger"] / 10) + "🟥" * round(
                            (self.stats["MAX_HUNGER"] - self.stats["hunger"]) / 10),
                        inline=False)
        embed.add_field(name="SLEEP: " + str(self.stats["sleep"]) + "/" + str(self.stats["MAX_SLEEP"]),
                        value="🟩" * round(self.stats["sleep"] / 10) + "🟥" * round(
                            (self.stats["MAX_SLEEP"] - self.stats["sleep"]) / 10),
                        inline=False)
        return embed

    # ------------------------------------ SETTERS ------------------------------------
    def add_health(self, value):
        self.stats["health"] += value
        self.stats["health"] = max(min(self.stats["health"], self.stats["MAX_HEALTH"]), 0)

        if self.stats["health"] == 0: self.state = States.DEAD

    def add_hunger(self, value):
        self.stats["hunger"] += value
        self.stats["hunger"] = max(min(self.stats["hunger"], self.stats["MAX_HUNGER"]), 0)

    def add_sleep(self, value):
        self.stats["sleep"] += value
        self.stats["sleep"] = max(min(self.stats["sleep"], self.stats["MAX_SLEEP"]), 0)

    def add_age(self, value):
        self.stats["age"] += value

    def set_state(self, state):
        self.state = state
