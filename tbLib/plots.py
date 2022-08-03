import asyncio
import json
import os
import discord

from tbLib.playerData import *
from tbLib.townsData import *
from tbLib.identifier import *
from tbLib.makeEmbed import makeEmbed


def calculateNextPlot(plotsOwned):
    return 250 * plotsOwned


def calculateNextStructurePrice(playerData, plottype):
    plottype = plottype.upper()
    if plottype not in ["MINE", "FOREST", "FARM", "POND"]:
        return -1
    plotCount = playerData[plottype + "S"]                      # + S to convert to plural form, i.e. MINE becomes MINES, etc.
    return 100 + (100 * (plotCount + 2) ** 2)


def makePlot(owner, plottype="PLAIN"):
    return {"OWNER": owner, "PLOTTYPE": plottype}


def plotIsValid(plot):
    if len(plot) != 2:
        return False
    if not 65 <= ord(plot[0]) <= 74:
        return False
    if not 48 <= ord(plot[1]) <= 57:
        return False
    return True


def userOwnsPlot(userID, townData, plot):
    if plot not in townData["PLOTS"]:
        return False
    return townData["PLOTS"][plot]["OWNER"] == str(userID)

def structureIsValid(structure):
    return structure in ["MINE", "FARM", "FOREST", "POND", "HOUSE"]

async def plotInfo(ctx, plot):
    plot = plot.upper()
    embed = makeEmbed()
    townID = getPlayerTown(ctx.author.id)
    if townID == "NONE":
        embed.color = discord.Color.red()
        embed.description = "You are not in a town!"
        await ctx.send(embed=embed)
        return
    if not plotIsValid(plot):
        embed.color = discord.Color.red()
        embed.description = "Invalid syntax! Syntax is `-plot info YX`, i.e. `-plot info C4`."
        await ctx.send(embed=embed)
        return
    townData = getTownData(townID)
    plotsData = townData["PLOTS"]
    if plot not in plotsData:
        embed.color = discord.Color.dark_gray()
        embed.description = "This plot is unclaimed."
        await ctx.send(embed=embed)
        return
    townName = townData["NAME"]
    plotType = plotsData[plot]["PLOTTYPE"]
    owner = getFullName(plotsData[plot]["OWNER"])
    embed.color = discord.Color.purple()
    embed.description = f"Plot **{plot}** in **{townName}**:\n\nOwner: **{owner}**\nStructure: **{plotType.capitalize()}**"
    await ctx.send(embed=embed)


def isAdjacentToTown(plot, plotsData):
    plotY = ord(plot[0])
    plotX = ord(plot[1])
    adjacentPlots = [(chr(plotY + 1) + chr(plotX)), (chr(plotY - 1) + chr(plotX)),
                     (chr(plotY) + chr(plotX + 1)), (chr(plotY) + chr(plotX - 1))]
    for adjPlot in adjacentPlots:
        if adjPlot in plotsData:
            return True
    return False


async def annexHandler(ctx, plot, client):
    plot = plot.upper()
    embed = makeEmbed()
    embed.color = discord.Color.red()
    townID = getPlayerTown(ctx.author.id)
    if townID == "NONE":
        embed.description = "You are not in a town!"
        await ctx.send(embed=embed)
        return
    if not plotIsValid(plot):
        embed.description = "Invalid syntax! Syntax is `-plot annex YX`, i.e. `-plot annex C4`."
        await ctx.send(embed=embed)
        return
    playerID = str(ctx.author.id)
    if not isMayor(playerID):
        embed.description = "Only the mayor can annex plots!"
        await ctx.send(embed=embed)
        return
    townData = getTownData(getPlayerTown(ctx.author.id))
    plotsData = townData["PLOTS"]
    if plot in plotsData:
        embed.description = "This plot already belongs to the town!"
        await ctx.send(embed=embed)
        return
    if not isAdjacentToTown(plot, plotsData):
        embed.description = "This plot is not adjacent to the town!"
        await ctx.send(embed=embed)
        return
    annexCost = calculateNextPlot(len(plotsData))
    playerData = getPlayerData(ctx.author.id)
    if playerData["BALANCE"] < annexCost:
        if not isAdjacentToTown(plot, plotsData):
            embed.description = f"You cannot afford this! A new plot will cost **${annexCost}**."
            await ctx.send(embed=embed)
            return
    embed.description = f"This will cost **${annexCost}** to annex. Are you sure?\n\nType `CONFIRM` to confirm"
    embed.color = discord.Color.teal()
    await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author

    try:
        msg = await client.wait_for("message", check=check, timeout=30)
    except asyncio.TimeoutError:
        embed.description = "Annex request timed out"
        await ctx.send(embed=embed)
        return
    if msg.content.upper() != "CONFIRM":
        embed.description = "Annex request cancelled."
        await ctx.send(embed=embed)
        return
    newPlot = makePlot(playerID)
    townData["PLOTS"][plot] = newPlot
    playerData["BALANCE"] -= annexCost
    setPlayerData(playerID, playerData)
    setTownData(townID, townData)
    embed.color = discord.Color.green()
    embed.description = "Plot annexed!"
    await ctx.send(embed=embed)
    return


async def buildHandler(ctx, plot, structure, client):
    plot = plot.upper()
    embed = makeEmbed()
    embed.color = discord.Color.red()
    townID = getPlayerTown(ctx.author.id)
    if townID == "NONE":
        embed.description = "You are not in a town!"
        await ctx.send(embed=embed)
        return
    if not plotIsValid(plot):
        embed.description = "Invalid syntax! Syntax is `-plot build <structure> YX`, i.e. `-plot build mine C4`."
        await ctx.send(embed=embed)
        return
    townData = getTownData(townID)
    if not userOwnsPlot(ctx.author.id, townData, plot):
        embed.description = "You don't own that plot!"
        await ctx.send(embed=embed)
        return
    currentStructure = townData["PLOTS"][plot]["PLOTTYPE"]
    if currentStructure != "PLAIN":
        embed.description = f"There is already a {currentStructure.lower()} on that plot!"
        await ctx.send(embed=embed)
        return
    playerData = getPlayerData(ctx.author.id)
    structure = structure.upper()
    structurePrice = calculateNextStructurePrice(playerData, structure)
    if structurePrice == -1:
        embed.description = "Invalid structure! Structures you can build are `mine`, `forest`, `farm`, and `pond`. Mayors can also build `house`."
        await ctx.send(embed=embed)
        return
    if playerData["BALANCE"] < structurePrice:
        embed.description = f"You Cannot afford that! The price to build a new **{structure.lower()}** is **${structurePrice}**."
        await ctx.send(embed=embed)
        return
    embed.description = f"This will cost **${structurePrice}** to build. Are you sure?\n\nType `CONFIRM` to confirm"
    embed.color = discord.Color.teal()
    await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author

    try:
        msg = await client.wait_for("message", check=check, timeout=30)
    except asyncio.TimeoutError:
        embed.description = "Build request timed out"
        await ctx.send(embed=embed)
        return
    if msg.content.upper() != "CONFIRM":
        embed.description = "Build request cancelled."
        await ctx.send(embed=embed)
        return
    townData["PLOTS"][plot]["PLOTTYPE"] = structure
    playerData["BALANCE"] -= structurePrice
    playerData[structure + "S"] += 1
    setTownData(townID, townData)
    setPlayerData(ctx.author.id, playerData)
    embed.description = f"{structure.capitalize()} built!"
    await ctx.send(embed=embed)
    return

