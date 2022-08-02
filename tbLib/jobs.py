import random
from math import ceil
import discord
import json
import time

from tbLib.makeEmbed import makeEmbed
from tbLib.playerData import *

waitTime = 10                                                           # specifies time to wait between commands


def calculateMoney(level, plots):                                       # calculates money to make based on level and plots owned.
    baseMoney = (20 + ceil(level ** 1.35)) * (1.2 ** plots)
    modifier = random.randint(85, 115) / 100
    return int(baseMoney * modifier)


def calculateXP(plots):                                                 # calculates xp based on plots owned
    baseXP = 10 * (1.5 ** plots)
    modifier = random.randint(85, 115) / 100
    return int(baseXP * modifier)


def calculateNextLevel(level):                                          # calculates required XP based on level
    return int(100 * level ** 1.2)


mineFlavor = ["While you were out mining, you saw a huge ore of gold! But, on closer look, it turned out to just be some yellow rock. Luckily, the next town over loves yellow rock!",
              "After mining all day looking for some copper, you come up empty! Oh well, the minecart full of emeralds and rubies will have to do.",
              "While mining some iron out, you wonder what this iron will be used for. However, as your pickaxe breaks from mining it, you suddenly know exactly what it will be used for.",
              "If you've ever wondered how much dynamite it takes to find gold, your research shows you will need at least a few dozen pounds.",
              "After the wheel on your minecart broke, you start to envy just how much gold you have to carry out.",
              "You’ve been mining for a couple hours and hit nothing, but before you turned home, you broke that last rock and hit the motherlode.",
              "When you were out mining in a new part of the mineshaft, you saw a rock that glew green under UV light. You sold it to a strange man rambling about bringing an end to this world.",
              "You found another person mining in the mineshaft, who broke a load-bearing rock. There was a small cave in on their position - but there was also a really cool looking rock that had just been unearthed. You only had time to save either the trapped miner or collect the rock before the rest of the area caved in. You sold the rock for a good buck.",
              "You really wanted to get some iron ore for a new pickaxe, but only found emeralds.",
              "You broke through the rock to find a massive underground civilization. An inhabitant slid you some cash to go the other direction and tell no one.",
              "Your oil lamp ran out of oil before you could exit. While bumbling around, by sheer luck, you happened upon a large deposit of gold."]
chopFlavor = ["You chopped down a tree and broke your axe. Luckily for you, there was a strangely axe-looking stick amidst the debris of the felled tree.",
              "While chopping a tree, an environmentalist came up to you and told you this tree had an exotic bird in it. They paid you to not chop it down.",
              "You chopped down a really big tree."]
farmFlavor = ["This year's harvest proved bountiful. You made an extra 2 loaves of bread.",
              "While out picking weeds, you found a beanstalk. It had 9 pea pods on it.",
              "Your barley choice was a good pick for this year, since corn had been ravaged by a disease and the livestock needed something to eat."]
fishFlavor = ["While out fishing, you only caught seaweed. Fortunately, a Sushi store just opened nearby and is short on seaweed.",
              "You felt a tug on your rod, and next thing you know you were flung into the pond. While you were flailing your arms everywhere, you managed to catch hold of a valuable trout.",
              "You reeled in your rod and caught a boot with a prehistoric seed in it. You sold it to the local museum.",
              "You reeled in your rod and caught an average size sunfish.",
              "You reeled in your rod and caught a single measly shrimp. After you placed it down, it exploded and got you some more valuable roe.",
              "You sat down for a couple hours and caught nothing. A fisherman who caught a sizable amount of fish at the same time felt bad, and gave you one of their fishes.",
              "You reeled in your rod and caught a cool looking fish.",
              "You reeled in your rod and caught the skeleton of a missing person. You called the police to give them this information and collected the bounty."]


async def mineHandler(ctx):
    await jobHandler(ctx, "LASTMINE", "MINELVL", "MINES", "MINEXP", random.choice(mineFlavor), discord.Color.teal())


async def chopHandler(ctx):
    await jobHandler(ctx, "LASTCHOP", "WOODLVL", "FORESTS", "WOODXP", random.choice(chopFlavor), discord.Color.purple())


async def harvestHandler(ctx):
    await jobHandler(ctx, "LASTHARVEST", "FARMLVL", "FARMS", "FARMXP", random.choice(farmFlavor), discord.Color.gold())


async def catchHandler(ctx):
    await jobHandler(ctx, "LASTCATCH", "FISHLVL", "PONDS", "FISHXP", random.choice(fishFlavor), discord.Color.blue())


async def jobHandler(ctx, timeToUse, level, plotName, xp, flavorText, sidebarColor):
    embed = makeEmbed()
    userID = ctx.author.id
    userData = getPlayerData(userID)                                    # fetches player data
    currentTime = int(time.time())                                      # gets current time
    timeSince = currentTime - userData[timeToUse]                       # calculates time since last input
    if timeSince < waitTime:                                            # if timeSince is too small, let player know how much more time to wait and return
        embed.description = f"You need to wait {waitTime - timeSince} more seconds before you mine again."
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return
    else:
        moneyMade = calculateMoney(userData[level], userData[plotName]) # calculates how much money to make
        xpMade = calculateXP(userData[plotName])                        # calculates how much xp to make
        embed.description = f"{flavorText}\nMade ${moneyMade} and gained {xpMade} xp."
        userData["BALANCE"] += moneyMade                                # gives player money
        userData[xp] += xpMade                                          # gives player xp
        while userData[xp] > calculateNextLevel(userData[level]):       # while the player has more money than the required XP to level up, level up
            userData[xp] -= calculateNextLevel(userData[level])
            userData[level] += 1
            embed.description += f"\n\n**LEVEL UP!!** You are now level " + str(userData[level]) + "."
        userData[timeToUse] = currentTime                               # set last time action was done
        setPlayerData(userID, userData)                                 # dump player data to their JSON file
        embed.set_footer(text="Level: " + str(userData[level]) + ", Progress: " + str(userData[xp]) + "/" + str(
            calculateNextLevel(userData[level])) + f". You now have ${getPlayerBalance(ctx.author.id)}.")                       # put level and xp progress in footer
        embed.color = sidebarColor
        await ctx.send(embed=embed)
