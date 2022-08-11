import asyncio
import random
from math import ceil
import discord
import json
import time

from tbLib.tbutils import makeEmbed
from tbLib.playerData import *
from tbLib.townsData import isMayor, getTownData

waitTime = 10                                                           # specifies time to wait between commands
scavengeWaitTime = 3600                                                 # specifies how long to wait between scavenges
scrambleTime = 30                                                       # specifies how long players have to unscramble the scavenge word


def calculateMoney(level, plots):                                       # calculates money to make based on level and plots owned.
    baseMoney = (20 + ceil(level ** 1.35)) * (1.2 ** plots)
    modifier = random.randint(85, 115) / 100
    return int(baseMoney * modifier)


def calculateXP(plots):                                                 # calculates xp based on plots owned
    baseXP = 10 * (1.5 ** plots)
    modifier = random.randint(85, 115) / 100
    return int(baseXP * modifier)


def calculateMayorBonus(playerID, structureType) -> float:              # provides a 10% bonus for every structure in the town
    if not isMayor(playerID):                                           # that correlates to the job done
        return 1
    townID = getPlayerTown(playerID)
    townData = getTownData(townID)
    structures = 0
    for plot in townData["PLOTS"]:
        if townData["PLOTS"][plot]["PLOTTYPE"] == structureType:
            structures += 1
    return 1 + (structures / 10)


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
scavengeFlavor = ["After following a treasure map an old man gave you, you found the X that marks the spot!",
                  "Though you had your doubts before buying this metal detector, it seems that it's already paid itself off!",
                  "You decided to take a trip to some ancient ruins, but you accidentally discovered a treasure room never seen before!",
                  "On your daily walk, you tripped and fell over something in the middle of the trail. You were upset over it until you looked at what exactly you tripped over.",
                  "It looks like your hours of digging random holes in the ground has paid off!"]
scavengeWords = ["GOLD", "SILVER", "DIAMONDS", "JEWELS", "EMERALDS", "JADE", "RUBIES", "RELIC", "CHEST", "PEARLS",
                 "NECKLACE", "BRACELET", "SAPPHIRE", "AMETHYST", "COINS", "CROWN", "EARRINGS", "TREASURE", "FORTUNE",
                 "GEMSTONES"]


async def mineHandler(ctx):
    await jobHandler(ctx, "mine", "LASTMINE", "MINELVL", "MINES", "MINEXP", random.choice(mineFlavor), discord.Color.teal())


async def chopHandler(ctx):
    await jobHandler(ctx, "chop", "LASTCHOP", "WOODLVL", "FORESTS", "WOODXP", random.choice(chopFlavor), discord.Color.purple())


async def harvestHandler(ctx):
    await jobHandler(ctx, "harvest", "LASTHARVEST", "FARMLVL", "FARMS", "FARMXP", random.choice(farmFlavor), discord.Color.gold())


async def catchHandler(ctx):
    await jobHandler(ctx, "catch", "LASTCATCH", "FISHLVL", "PONDS", "FISHXP", random.choice(fishFlavor), discord.Color.blue())


async def jobHandler(ctx, job, timeToUse, level, plotName, xp, flavorText, sidebarColor):
    embed = makeEmbed()
    playerID = str(ctx.author.id)
    playerData = getPlayerData(playerID)                                # fetches player data
    currentTime = int(time.time())                                      # gets current time
    timeSince = currentTime - playerData[timeToUse]                     # calculates time since last input
    if timeSince < waitTime:                                            # if timeSince is too small, let player know how much more time to wait and return
        embed.description = f"You need to wait {waitTime - timeSince} more seconds before you {job} again."
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return
    moneyMade = calculateMoney(playerData[level], playerData[plotName]) # calculates how much money to make
    if isMayor(playerID):
        moneyMade = int(moneyMade * calculateMayorBonus(playerID, plotName[0:-1]))
    xpMade = calculateXP(playerData[plotName])                        # calculates how much xp to make
    embed.description = f"{flavorText}\nMade ${moneyMade} and gained {xpMade} xp."
    playerData["BALANCE"] += moneyMade                                  # gives player money

    playerData[xp] += xpMade                                            # gives player xp
    while playerData[xp] > calculateNextLevel(playerData[level]):       # while the player has more money than the required XP to level up, level up
        playerData[xp] -= calculateNextLevel(playerData[level])
        playerData[level] += 1
        embed.description += f"\n\n**LEVEL UP!!** You are now level " + str(playerData[level]) + "."
    playerData[timeToUse] = currentTime                                 # set last time action was done
    setPlayerData(playerID, playerData)                                 # dump player data to their JSON file
    embed.set_footer(text="Level: " + str(playerData[level]) + ", Progress: " + str(playerData[xp]) + "/" + str(
        calculateNextLevel(playerData[level])) + f". You now have ${getPlayerBalance(ctx.author.id)}.")                       # put level and xp progress in footer
    embed.color = sidebarColor
    await ctx.send(embed=embed)


async def scavengeHandler(ctx, client):
    embed = makeEmbed()
    playerID = str(ctx.author.id)
    playerData = getPlayerData(playerID)                                # fetches player data
    playerName = playerData["NAME"]                                     # gets player name for messages, reduces confusion when multiple players are using the bot at the same time
    currentTime = int(time.time())
    timeLeft = scavengeWaitTime - (currentTime - playerData["LASTSCAVENGE"])        # calculates time in seconds between now and last scavenge time and how much time left to wait
    if timeLeft > 0:                                                    # scavenge cooldown still in effect
        embed.color = discord.Color.red()
        embed.description = f"You cannot scavenge for another {int(timeLeft / 60)} minutes, {timeLeft % 60} seconds."
        await ctx.send(embed=embed)
        return
    flavorText = random.choice(scavengeFlavor)                          # gets a random flavor text
    treasure = random.choice(scavengeWords)                             # picks a treasure word
    scrambedTreasure = scrambleWord(treasure)                           # scrambles the word
    embed.description = f"{flavorText}\n\nUnscramble this word to get what you discovered: **{scrambedTreasure}**"
    embed.set_footer(text=f"You have {scrambleTime} seconds to unscramble!.")
    embed.color = discord.Color.green()
    await ctx.send(embed=embed)
    embed = makeEmbed()
    timeOut = currentTime + scrambleTime
    def check(m):                                                       # defines when a bot should stop waiting for input
        return m.author == ctx.author
    guessedCorrectly = False
    while not guessedCorrectly:                                         # continues asking for answer until player gets it or time runs out
        try:
            msg = await client.wait_for("message", check=check, timeout=timeOut - int(time.time())) #timer is based on time when the command started and current time, does not reset on wrong guess
        except asyncio.TimeoutError:                                    # cancels command when time runs out
            embed.color = discord.Color.red()
            embed.description = f"**{playerName}**, You ran out of time. Try again!"
            await ctx.send(embed=embed)
            return
        if msg.content.upper() != treasure:                             # asks to retry when guess is incorrect
            embed.color = discord.Color.dark_orange()
            embed.description = f"**{playerName}**, That's not correct! You have {timeOut - int(time.time())} seconds left. The scrambled word is **{scrambedTreasure}**."
            await ctx.send(embed=embed)
        else:
            guessedCorrectly = True
    embed = makeEmbed()                                                 # this code only runs if player unscrambles word before the time runs out
    moneyMade = int(800 * random.randint(85, 115) / 100)                # money made is $800 +/- 15%
    embed.color = discord.Color.green()
    embed.description = f"**{playerName}**, You guessed it correctly! You made **${moneyMade}**."
    playerData["BALANCE"] += moneyMade                                  # pays player
    playerData["LASTSCAVENGE"] = currentTime                            # resets the scavenger time to restart cooldown
    setPlayerData(playerID, playerData)                                 # sets player date
    await ctx.send(embed=embed)
    return


def scrambleWord(word):                                                 # given a word, scrambles the letters in the word
    charList = list(word)                                               # makes a list of characters
    wordLen = len(word) - 1
    for i in range(100):                                                # swaps one random character with another 100 times
        index1 = random.randint(0, wordLen)
        index2 = random.randint(0, wordLen)
        tempChar = charList[index1]
        charList[index1] = charList[index2]
        charList[index2] = tempChar
    scrambled = ""
    for char in charList:                                               # puts word back together
        scrambled += char
    return scrambled
