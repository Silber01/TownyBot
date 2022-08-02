import asyncio
import json
import os
import discord

from tbLib.playerData import *
from tbLib.townsData import *
from tbLib.identifier import *
from tbLib.makeEmbed import makeEmbed


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


def calculateNextPlot(plotsOwned):
    return 250 * plotsOwned


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
    embed = makeEmbed()
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

