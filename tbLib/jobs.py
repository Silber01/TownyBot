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
              "After the wheel on your minecart broke, you start to envy just how much gold you have to carry out."]

async def mineHandler(ctx):
    await jobHandler(ctx, "LASTMINE", "MINELVL", "MINES", "MINEXP", random.choice(mineFlavor), discord.Color.teal())


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
        embed.set_footer(text="Level: " + str(userData[level]) + ", Progress: " + str(userData[xp]) + "/" + str(
            calculateNextLevel(userData[level])) + f". You now have ${getPlayerBalance(ctx.author.id)}.")                       # put level and xp progress in footer
        embed.color = sidebarColor
        userData[timeToUse] = currentTime  # set last time action was done
        setPlayerData(userID, userData)  # dump player data to their JSON file
        await ctx.send(embed=embed)
