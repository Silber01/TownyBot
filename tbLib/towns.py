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
from tbLib.makeMap import makeForSaleMap, makeOwnerMap, makeMap, getMap
from tbLib.identifier import identify, getFullName
from tbLib.plots import makePlot, calculateNextPlot

townCost = 25000
plainText = "PLAIN"
mineTest = "MINE"
forestText = "FOREST"
farmText = "FARM"
pondText = "POND"
houseText = "HOUSE"
forsaleText = "FORSALE"
houseforsaleText = "HOUSEFORSALE"


async def townsHelp(ctx):
    await ctx.send("I'll implement this help screen later")


async def townInfoHandler(ctx, name="NONE"):
    embed = makeEmbed()
    embed.color = discord.Color.red()
    if name == "NONE":
        townID = getPlayerTown(ctx.author.id)
        if townID is None:
            embed.description = "You are not in a town!"
            await ctx.send(embed=embed)
            return
    else:
        townID = findTownID(name)
        if townID is None:
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
    residents = []
    for resident in townData["RESIDENTS"]:
        residents.append(getPlayerData(resident)["NAME"])
    embed.color = discord.Color.purple()
    embed.description = f"""Information for **{townName}**:\n\nMayor: **{getFullName(townMayor)}**\nAmount of plots: **{townSize}**\nResidents: {str(residents)[1:-1].replace("'", "")}\n\n
                            Taxes per plot owned: **${townTax}**/day\nPrice to own a plot: **${plotPrice}**
                            \nPrice to annex a plot: **${calculateNextPlot(townSize)}**
                            \n\nDo `-town map {townName}` to see a map of this town!"""
    await ctx.send(embed=embed)


async def newTownHandler(ctx, name="NONE"):
    playerID = str(ctx.author.id)
    playerData = getPlayerData(playerID)
    embed = makeEmbed()
    embed.color = discord.Color.red()
    if not playerData["TOWN"] is None:
        embed.description = "You are already in a town!"
        await ctx.send(embed=embed)
        return
    if playerData["BALANCE"] < townCost:
        embed.description = f"You cannot afford a town! Towns cost ${townCost}."
        await ctx.send(embed=embed)
        return
    townID = secrets.token_hex(16)
    if name == "NONE":
        name = generateName()
    if not findTownID(name) is None:
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
    townData["PLOTS"][housePlot] = makePlot(playerID, houseText)
    townData["RESIDENTS"].append(playerID)
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
    evicted = getTownData(townID)["RESIDENTS"]
    for user in evicted:
        userData = getPlayerData(user)
        userData["TOWN"] = None
        userData["PLOTS"] = 0
        userData["MINES"] = 0
        userData["FARMS"] = 0
        userData["FORESTS"] = 0
        userData["PONDS"] = 0
        setPlayerData(user, userData)
    os.remove(f"towns/{townID}.json")
    embed.description = f"{townName} has fallen! The following people are now homeless:\n"
    for user in evicted:
        embed.description += getFullName(user) + "\n"
    await ctx.send(embed=embed)


async def renameHandler(ctx, name):
    embed = makeEmbed()
    if not isMayor:
        embed.description = "You don't own a town!"
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return
    townID = getPlayerTown(ctx.author.id)
    townData = getTownData(townID)
    townData["NAME"] = name
    setTownData(townID, townData)
    embed.description = "Town renamed!"
    embed.color = discord.Color.green()
    await ctx.send(embed=embed)
    return


async def makeMapHandler(ctx, town="NONE"):
    if not await canMakeMap(ctx):
        return
    townFile = await getMap(ctx, town, "MAP")
    if townFile is None:
        return
    await ctx.send(file=discord.File(townFile))
    os.remove(str(townFile))


async def makeForSaleMapHandler(ctx, town="NONE"):
    if not await canMakeMap(ctx):
        return
    townFile = await getMap(ctx, town, "FORSALE")
    if townFile is None:
        return
    await ctx.send(file=discord.File(townFile))
    os.remove(str(townFile))


async def leaveHandler(ctx, client):
    embed = makeEmbed()
    embed.color = discord.Color.red()
    playerID = str(ctx.author.id)
    townID = getPlayerTown(playerID)
    if townID is None:
        embed.description = "You are already not in a town!"
        await ctx.send(embed=embed)
        return
    if isMayor(playerID):
        embed.description = "You cannot leave a town you own! Appoint another mayor using `-town set mayor` or delete the town using `-town delete`."
        await ctx.send(embed=embed)
        return
    embed.description = """Are you sure you want to leave your town? Your plots will be gone forever!\n\nType `CONFIRM` to confirm"""
    await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author

    try:
        msg = await client.wait_for("message", check=check, timeout=30)
    except asyncio.TimeoutError:
        embed.description = "Town leave request timed out."
        await ctx.send(embed=embed)
        return
    if msg.content.upper() != "CONFIRM":
        embed.description = "Town leave request cancelled."
        await ctx.send(embed=embed)
        return
    clearUserLand(ctx)
    embed.description = "You left town."
    await ctx.send(embed=embed)


def clearUserLand(ctx):
    playerID = str(ctx.author.id)
    playerData = getPlayerData(playerID)
    playerData["TOWN"] = None
    playerData["PLOTS"] = 0
    playerData["MINES"] = 0
    playerData["FORESTS"] = 0
    playerData["FARMS"] = 0
    playerData["PONDS"] = 0
    townID = getPlayerTown(playerID)
    townData = getTownData(townID)
    mayorID = townData["MAYOR"]
    townData["RESIDENTS"].remove(playerID)
    for plot in townData["PLOTS"]:
        if townData["PLOTS"][plot]["OWNER"] == playerID:
            plotInfo = townData["PLOTS"][plot]
            plotInfo["OWNER"] = mayorID
            if plotInfo["PLOTTYPE"] not in [houseText, plainText]:
                plotInfo["PLOTTYPE"] = plainText
            townData["PLOTS"][plot] = plotInfo
    setTownData(townID, townData)
    setPlayerData(playerID, playerData)


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
    if townID is None:
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
