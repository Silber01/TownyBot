import json
import os
import discord

from tbLib.playerData import *
from tbLib.townsData import *
from tbLib.identifier import *
from tbLib.makeEmbed import makeEmbed


def plotIsValid(plot):
    if len(plot) != 2:
        return False
    if not 65 <= ord(plot[0]) <= 74:
        return False
    if not 48 <= ord(plot[1]) <= 57:
        return False
    return True


async def plotInfo(ctx, plot):
    plot = plot.upper()
    embed = makeEmbed()
    if not plotIsValid(plot):
        embed.color = discord.Color.red()
        embed.description = "Invalid syntax! Syntax is `plot YX`, i.e. `plot C4`."
        await ctx.send(embed=embed)
        return
    townData = getTownData(getPlayerTown(ctx.author.id))
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

async def annexHandler(ctx, plot):
    await ctx.send("TODO")
