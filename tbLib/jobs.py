import asyncio
import os
import random
from math import ceil
import discord
import json
import time

from tbLib.tbutils import makeEmbed, formatNum
from tbLib.playerData import *
from tbLib.townsData import isMayor, getTownData

waitTime = 10                                                           # specifies time to wait between commands
waitPenalty = 120
scavengeWaitTime = 3600                                                 # specifies how long to wait between scavenges
scrambleTime = 30                                                       # specifies how long players have to unscramble the scavenge word


def calculateMoney(level, plots):                                       # calculates money to make based on level and plots owned.
    baseMoney = (20 + ceil(level ** 1.35)) * (1.1 ** plots)
    modifier = random.randint(85, 115) / 100
    return int(baseMoney * modifier)


def calculateXP(plots):                                                 # calculates xp based on plots owned
    baseXP = 10 * (1.35 ** plots)
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


scavengeFlavor = ["After following a treasure map an old man gave you, you found the X that marks the spot!",
                  "Though you had your doubts before buying this metal detector, it seems that it's already paid itself off!",
                  "You decided to take a trip to some ancient ruins, but you accidentally discovered a treasure room never seen before!",
                  "On your daily walk, you tripped and fell over something in the middle of the trail. You were upset over it until you looked at what exactly you tripped over.",
                  "It looks like your hours of digging random holes in the ground has paid off!"]
scavengeWords = ["GOLD", "SILVER", "DIAMONDS", "JEWELS", "EMERALDS", "JADE", "RUBIES", "RELIC", "CHEST", "PEARLS",
                 "NECKLACE", "BRACELET", "SAPPHIRE", "AMETHYST", "COINS", "CROWN", "EARRINGS", "TREASURE", "FORTUNE",
                 "GEMSTONES"]


async def mineHandler(ctx):
    await jobHandler(ctx, "MINE", discord.Color.teal())


async def chopHandler(ctx):
    await jobHandler(ctx, "CHOP", discord.Color.purple())


async def harvestHandler(ctx):
    await jobHandler(ctx, "FARM", discord.Color.gold())


async def catchHandler(ctx):
    await jobHandler(ctx, "FISH", discord.Color.blue())


async def jobHandler(ctx, job, sidebarColor):
    embed = makeEmbed()
    playerID = str(ctx.author.id)
    if f"{playerID}.json" in os.listdir("sellList"):                    # if the player has something to sell, they can't do jobs until they sell it
        with open(f"sellList/{playerID}.json", "r") as readFile:
            sellWord = json.load(readFile)["WORD"].lower()
        embed.description = f"You can't mine until you sell your {sellWord}! Do `-sell {sellWord}` to continue doing jobs."
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return
    playerData = getPlayerData(playerID)                                # fetches player data
    currentTime = int(time.time())                                      # gets current time
    with open("non-code/jobs.json", "r") as readFile:
        jobInfo = json.load(readFile)[job]
    flavorText = random.choice(jobInfo["FLAVOR"])                       # gets data from the appropriate job information
    level = jobInfo["LEVEL"]
    plotName = jobInfo["STRUCTURE"] + "S"
    xp = jobInfo["XP"]
    timeToUse = jobInfo["TIMETOUSE"]
    timeSince = currentTime - playerData[timeToUse]                     # calculates time since last input
    if timeSince < waitTime:                                            # if timeSince is too small, let player know how much more time to wait and return
        embed.description = f"You need to wait {waitTime - timeSince} more seconds before you {job.lower()} again."
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return
    moneyMade = calculateMoney(playerData[level], playerData[plotName]) # calculates how much money to make
    if isMayor(playerID):
        moneyMade = int(moneyMade * calculateMayorBonus(playerID, plotName[0:-1]))
    xpMade = calculateXP(playerData[plotName])                        # calculates how much xp to make
    embed.description = f"{flavorText}\nMade ${formatNum(moneyMade)} and gained {formatNum(xpMade)} xp."
    playerData["BALANCE"] += moneyMade                                  # gives player money
    playerData[xp] += xpMade                                            # gives player xp
    while playerData[xp] > calculateNextLevel(playerData[level]):       # while the player has more money than the required XP to level up, level up
        playerData[xp] -= calculateNextLevel(playerData[level])
        playerData[level] += 1
        embed.description += f"\n\n**LEVEL UP!!** You are now level " + str(playerData[level]) + "."
    playerData[timeToUse] = currentTime                                 # set last time action was done
    setPlayerData(playerID, playerData)                                 # dump player data to their JSON file
    embed.set_footer(text="Level: " + str(playerData[level]) + ", Progress: " + str(playerData[xp]) + "/" + str(
        calculateNextLevel(playerData[level])) + f". You now have ${formatNum(getPlayerBalance(ctx.author.id))}.")                       # put level and xp progress in footer
    embed.color = sidebarColor
    if random.randint(1, 50) == 1:                                      # chance to find something to sell
        sellText = jobInfo["SELLTEXT"]
        sellWord = random.choice(jobInfo["SELLITEMS"])
        embed.description += "\n\n**WARNING**\n" + sellText
        embed.description += f"\n\n**Do `-sell {sellWord.lower()}` to sell your {sellWord.lower()}**."
        embed.color = discord.Color.dark_orange()
        makeSell(playerID, sellWord, job, timeToUse)                    # makes a sell order with a word appropriate to the job that triggered it
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
            embed.description = f"**{playerName}**, You ran out of time. The word was **{treasure}**. Try again!"
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
    embed.description = f"**{playerName}**, You guessed it correctly! You made **${formatNum(moneyMade)}**."
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


def makeSell(playerID, word, job, jobTimer):                            # makes a sell file with word, job, and timer to use
    sellData = {"WORD": word,
                "JOB": job,
                "JOBTIMER": jobTimer}
    with open(f"sellList/{playerID}.json", "w") as writeFile:
        json.dump(sellData, writeFile)


async def sellHandler(ctx, word="NONE"):                                # handles selling items when necessary
    embed = makeEmbed()
    embed.color = discord.Color.red()
    if word == "NONE":                                                  # the user did not specify a word
        embed.description = "Invalid syntax! Syntax is `-sell <item>`. Make sure you have an item to sell from doing jobs!"
        await ctx.send(embed=embed)
        return
    playerID = str(ctx.author.id)
    if f"{playerID}.json" not in os.listdir("sellList"):                # if the player does not have any file in sellList
        embed.description = "You do not have anything to sell!"
        await ctx.send(embed=embed)
        return
    with open(f"sellList/{playerID}.json", "r") as readFile:            # gets sellList data
        sellData = json.load(readFile)
    sellWord = sellData["WORD"]
    os.remove(f"sellList/{playerID}.json")
    playerData = getPlayerData(playerID)
    if word.upper() == sellWord.upper():                                # if word is entered correctly, pay user
        moneyMade = int(800 * random.randint(85, 115) / 100)  # money made is $800 +/- 15%
        embed.description = f"You sold your {sellWord.lower()} for **${moneyMade}**!"
        embed.color = discord.Color.green()
        playerData["BALANCE"] += moneyMade
    else:                                                               # if word is not entered correctly, make them wait 2 minutes before doing that job again
        job = sellData["JOB"]
        timeToUse = sellData["JOBTIMER"]
        embed.description = f"""You sold the wrong item! You were supposed to sell **{sellWord.lower()}**! 
                            After arguing with the angry shopkeeper, you can't {job.lower()} for another 2 minutes!"""
        embed.color = discord.Color.red()
        playerData[timeToUse] = int(time.time()) + 120
    await ctx.send(embed=embed)
    setPlayerData(playerID, playerData)
