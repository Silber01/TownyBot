import asyncio
import os
import json
import random
import time

import discord
import secrets

from tbLib.playerData import *
from tbLib.makeEmbed import makeEmbed
from tbLib.nameGenerator import generateName
from tbLib.townsData import *
from tbLib.makeMap import makeForSaleMap, makeOwnerMap, makeMap
from tbLib.identifier import identify, getFullName
from tbLib.plots import makePlot, calculateNextPlot

townCost = 25000
plainText = "PLAIN"
mineTest = "MINE"
forestText = "FOREST"
farmText = "FARM"
pondText = "POND"
housesText = "HOUSES"


async def townsHelp(ctx):
    await ctx.send("I'll implement this help screen later")


async def townInfoHandler(ctx, name="NONE"):
    embed = makeEmbed()
    embed.color = discord.Color.red()
    if name == "NONE":
        townID = getPlayerTown(ctx.author.id)
        if townID == "NONE":
            embed.description = "You are not in a town!"
            await ctx.send(embed=embed)
            return
    else:
        townID = findTownID(name)
        if townID == "NONE":
            embed = makeEmbed()
            embed.description = "That town does not exist!"
            await ctx.send(embed=embed)
            return
    townData = getTownData(townID)
    townName = townData["NAME"]
    townMayor = townData["MAYOR"]
    townTax = townData["PLOTTAX"]
    plotPrice = townData["PLOTPRICE"]
    townSize = len(townData["PLOTS"])
    embed.color = discord.Color.purple()
    embed.description = f"""Information for **{townName}**:\n\nMayor: **{getFullName(townMayor)}**\nAmount of plots: **{townSize}**\n\n
                            Taxes per plot owned: **${townTax}**/day\nPrice to own a plot: **${plotPrice}**
                            \nPrice to annex a plot: **${calculateNextPlot(townSize)}**
                            \n\nDo `-town map {townName}` to see a map of this town!"""
    await ctx.send(embed=embed)


async def newTownHandler(ctx, name="NONE"):
    playerID = str(ctx.author.id)
    playerData = getPlayerData(playerID)
    embed = makeEmbed()
    embed.color = discord.Color.red()
    if playerData["TOWN"] != "NONE":
        embed.description = "You are already in a town!"
        await ctx.send(embed=embed)
        return
    if playerData["BALANCE"] < townCost:
        embed.description = f"You cannot afford a town! Towns cost ${townCost}."
        await ctx.send(embed=embed)
        return
    townID = secrets.token_hex(16)
    if name == "NONE":
        townName = generateName()
    if findTownID(name) != "NONE":
        embed.description = f"There is already a town with this name!"
        await ctx.send(embed=embed)
        return
    else:
        townName = name
    with open(f"non-code/inittown.json", "r") as read_file:
        townData = json.load(read_file)
    townData["NAME"] = townName
    townData["MAYOR"] = playerID
    starterPlots = ["E4", "E5", "F4", "F5"]
    for plot in starterPlots:
        townData["PLOTS"][plot] = makePlot(playerID, plainText)
    housePlot = random.choice(starterPlots)
    townData["PLOTS"][housePlot] = makePlot(playerID, housesText)
    setTownData(townID, townData)
    playerData["BALANCE"] -= townCost
    playerData["TOWN"] = townID
    playerData["PLOTS"] += 4
    setPlayerData(playerID, playerData)
    embed.description = f"**__NEW TOWN MADE__**\n Your new town name is {townName}!"
    embed.color = discord.Color.green()
    await ctx.send(embed=embed)


async def deleteTownHandler(ctx, client):
    embed = makeEmbed()
    userID = str(ctx.author.id)
    if not isMayor(userID):
        embed.description = "You do not own a town!"
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return
    embed.color = discord.Color.dark_orange()
    embed.description = """Are you sure you want to delete your town? Your plots and your resident's plots will be gone forever!\n\nType `DELETE` to confirm"""
    await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author
    try:
        msg = await client.wait_for("message", check=check, timeout=30)
    except asyncio.TimeoutError:
        embed.description = "Town deletion request timed out."
        await ctx.send(embed=embed)
        return
    if msg.content.upper() != "DELETE":
        embed.description = "Town deletion request cancelled."
        await ctx.send(embed=embed)
        return
    townID = getPlayerData(ctx.author.id)["TOWN"]
    townName = getTownName(townID)
    evicted = []
    for user in os.listdir("players"):
        userID = user.replace(".json", "")
        userData = getPlayerData(userID)
        if userData["TOWN"] == townID:
            userData["TOWN"] = "NONE"
            userData["PLOTS"] = 0
            userData["MINES"] = 0
            userData["FARMS"] = 0
            userData["FORESTS"] = 0
            userData["PONDS"] = 0
            setPlayerData(userID, userData)
            evicted.append(userData["NAME"] + "#" + userData["DISCRIMINATOR"])
    os.remove(f"towns/{townID}.json")
    embed.description = f"{townName} has fallen! The following people are now homeless:\n"
    for user in evicted:
        embed.description += user + "\n"
    await ctx.send(embed=embed)


async def makeMapHandler(ctx, town="NONE"):
    if not await canMakeMap(ctx):
        return
    if town == "NONE":
        townID = getPlayerTown(ctx.author.id)
    else:
        townID = findTownID(town)
    if townID == "NONE":
        embed = makeEmbed()
        embed.description = "This town doesn't exist!"
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return
    townFile = makeMap(townID)
    await ctx.send(file=discord.File(townFile))
    os.remove(townFile)


async def makeForSaleMapHandler(ctx, town="NONE"):
    if not await canMakeMap(ctx):
        return
    if town == "NONE":
        townID = getPlayerTown(ctx.author.id)
    else:
        townID = findTownID(town)
    if townID == "NONE":
        embed = makeEmbed()
        embed.description = "This town doesn't exist!"
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return
    townFile = makeForSaleMap(townID)
    await ctx.send(file=discord.File(townFile))
    os.remove(townFile)


async def makeOwnerMapHandler(ctx, resident="NONE"):
    if not await canMakeMap(ctx):
        return
    if resident == "NONE":
        residentID = str(ctx.author.id)
    else:
        residentID = identify(resident)
        if residentID.startswith("ERROR"):
            embed = makeEmbed()
            embed.description = residentID.replace("ERROR ", "")
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
    townID = getPlayerTown(residentID)
    if townID == "NONE":
        embed = makeEmbed()
        embed.description = "This person is not in a town!"
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return
    townFile = makeOwnerMap(townID, residentID)
    await ctx.send(file=discord.File(townFile))
    os.remove(townFile)


async def canMakeMap(ctx):
    mapTimer = 3
    playerData = getPlayerData(ctx.author.id)
    lastMap = int(time.time()) - playerData["LASTMAP"]
    if lastMap < mapTimer:
        embed = makeEmbed()
        embed.color = discord.Color.red()
        embed.description = f"You must wait {mapTimer - lastMap} more seconds to make a map."
        await ctx.send(embed=embed)
        return False
    playerData["LASTMAP"] = int(time.time())
    setPlayerData(ctx.author.id, playerData)
    return True
