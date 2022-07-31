import random
from math import ceil
import discord
import json
import time

from tbLib.makeEmbed import makeEmbed

waitTime = 10


def calculateMoney(level, plots):
    baseMoney = (20 + ceil(level ** 1.35)) * (1.2 ** plots)
    modifier = random.randint(85, 115) / 100
    return int(baseMoney * modifier)


def calculateXP(plots):
    baseXP = 10 * (1.5 ** plots)
    modifier = random.randint(85, 115) / 100
    return int(baseXP * modifier)


def calculateNextLevel(level):
    return int(100 * level ** 1.2)


async def mineHandler(ctx):
    await jobHandler(ctx, "LASTMINE", "MINELVL", "MINES", "MINEXP", "You mined.", discord.Color.teal())


async def chopHandler(ctx):
    await jobHandler(ctx, "LASTCHOP", "WOODLVL", "FORESTS", "WOODXP", "You cut some wood.", discord.Color.purple())


async def harvestHandler(ctx):
    await jobHandler(ctx, "LASTHARVEST", "FARMLVL", "FARMS", "FARMXP", "You harvested some crops.",
                     discord.Color.gold())


async def catchHandler(ctx):
    await jobHandler(ctx, "LASTCATCH", "FISHLVL", "PONDS", "FISHXP", "You caught a fish.", discord.Color.blue())


async def jobHandler(ctx, timeToUse, level, plotName, xp, flavorText, sidebarColor):
    embed = makeEmbed()
    userID = ctx.author.id
    with open(f"players/{userID}.json", "r") as read_file:
        userData = json.load(read_file)
    currentTime = int(time.time())
    timeSince = currentTime - userData[timeToUse]
    if timeSince < waitTime:
        embed.description = f"You need to wait {waitTime - timeSince} more seconds before you mine again."
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return
    else:
        moneyMade = calculateMoney(userData[level], userData[plotName])
        xpMade = calculateXP(userData[plotName])
        embed.description = f"{flavorText}\nMade ${moneyMade} and gained {xpMade} xp."
        userData["BALANCE"] += moneyMade
        userData[xp] += xpMade
        while userData[xp] > calculateNextLevel(userData[level]):
            userData[xp] -= calculateNextLevel(userData[level])
            userData[level] += 1
            embed.description += f"\n\n**LEVEL UP!!** You are now level " + str(userData[level]) + "."
        embed.set_footer(text="Level: " + str(userData[level]) + ", Progress: " + str(userData[xp]) + "/" + str(
            calculateNextLevel(userData[level])))
        embed.color = sidebarColor
        await ctx.send(embed=embed)
        userData[timeToUse] = currentTime
        with open(f"players/{userID}.json", "w") as write_file:
            json.dump(userData, write_file)
