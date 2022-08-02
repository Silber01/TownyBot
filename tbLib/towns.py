import os
import json
import time

import discord
import secrets

from tbLib.playerData import *
from tbLib.makeEmbed import makeEmbed
from tbLib.nameGenerator import generateName
from tbLib.townsData import *
from tbLib.makeMap import makeForSaleMap, makeOwnerMap, makeMap
from tbLib.identifier import identify

townCost = 25000
plainText = "PLAIN"
mineTest = "MINE"
forestText = "FOREST"
farmText = "FARM"
pondText = "POND"
housesText = "HOUSES"


def makePlot(owner, plottype):
    return {"OWNER": owner, "PLOTTYPE": plottype}


async def townsHelp(ctx):
    await ctx.send("I'll implement this help screen later")


async def newTown(ctx, name="NONE"):
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
    else:
        townName = name
    with open(f"non-code/inittown.json", "r") as read_file:
        townData = json.load(read_file)
    townData["NAME"] = townName
    townData["MAYOR"] = playerID
    starterPlots = ["E4", "E5", "F4", "F5"]
    for plot in starterPlots:
        townData["PLOTS"][plot] = makePlot(playerID, plainText)
    setTownData(townID, townData)
    playerData["BALANCE"] -= townCost
    playerData["TOWN"] = townID
    setPlayerData(playerID, playerData)
    embed.description = f"**__NEW TOWN MADE__**\n Your new town name is {townName}!"
    embed.color = discord.Color.green()
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
        embed.description = "This town doesn't exist!"
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
