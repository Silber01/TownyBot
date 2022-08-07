import discord

from tbLib.playerData import *
from tbLib.townsData import *
from tbLib.identifier import *
from tbLib.makeEmbed import makeEmbed
from tbLib.tbutils import warnUser

houseCost = 1000
plainText = "PLAIN"
mineText = "MINE"
forestText = "FOREST"
farmText = "FARM"
pondText = "POND"
houseText = "HOUSE"
forsaleText = "FORSALE"
houseforsaleText = "HOUSEFORSALE"


def countHousesOwned(playerID):
    townID = getPlayerTown(playerID)
    townData = getTownData(townID)
    houseCount = 0
    for plot in townData["PLOTS"]:
        plotData = townData["PLOTS"][plot]
        if str(plotData["OWNER"]) == playerID and plotData["PLOTTYPE"] == houseText:
            houseCount += 1
    return houseCount


async def isInTown(ctx):
    townID = getPlayerTown(ctx.author.id)
    if townID is None:
        embed = makeEmbed()
        embed.description = "You are not in a town!"
        await ctx.send(embed=embed)
        return False
    return True


def calculateNextPlot(plotsOwned):
    return 250 * plotsOwned


def calculateNextStructurePrice(playerData, plottype):
    plottype = plottype.upper()
    if plottype not in [mineText, forestText, farmText, pondText]:
        return -1
    plotCount = playerData[plottype + "S"]  # + S to convert to plural form, i.e. MINE becomes MINES, etc.
    return int(100 * (2 ** (plotCount + 2)))


def makePlot(owner, plottype=plainText):
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
    if structure in [mineText, forestText, farmText, pondText, houseText]:
        return True
    return False


async def plotInfo(ctx, plot):
    if not await isInTown(ctx):
        return
    plot = plot.upper()
    embed = makeEmbed()
    townID = getPlayerTown(ctx.author.id)
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
    if plotsData[plot]["OWNER"] is None:
        embed.color = discord.Color.dark_gray()
        embed.description = "This plot is for sale."
        await ctx.send(embed=embed)
        return
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
    if not await isInTown(ctx):
        return
    plot = plot.upper()
    embed = makeEmbed()
    embed.color = discord.Color.red()
    townID = getPlayerTown(ctx.author.id)
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
        embed.description = f"You cannot afford this! A new plot will cost **${annexCost}**."
        await ctx.send(embed=embed)
        return
    warnText = f"This will cost **${annexCost}** to annex. Are you sure?\n\nType `CONFIRM` to confirm"
    timeOutText = "Annex request timed out"
    cancelMsg = "Annex request cancelled."
    if not await warnUser(ctx, client, warnText, cancelMsg, timeOutText, 30, "CONFIRM"):
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
    if not await isInTown(ctx):
        return
    plot = plot.upper()
    embed = makeEmbed()
    embed.color = discord.Color.red()
    townID = getPlayerTown(ctx.author.id)
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
    if currentStructure != plainText:
        embed.description = f"There is already a {currentStructure.lower()} on that plot!"
        await ctx.send(embed=embed)
        return
    structure = structure.upper()
    if not structureIsValid(structure):
        embed.description = "Invalid structure! Structures you can build are `mine`, `forest`, `farm`, and `pond`. Mayors can also build `house`."
        await ctx.send(embed=embed)
        return
    playerData = getPlayerData(ctx.author.id)
    if structure == houseText:
        if not isMayor(str(ctx.author.id)):
            embed.description = "You need to be a mayor to build a house!"
            await ctx.send(embed=embed)
            return
        structurePrice = 1000
    else:
        structurePrice = calculateNextStructurePrice(playerData, structure)
    if playerData["BALANCE"] < structurePrice:
        embed.description = f"You Cannot afford that! The price to build a new **{structure.lower()}** is **${structurePrice}**."
        await ctx.send(embed=embed)
        return
    warnText = f"This will cost **${structurePrice}** to build. Are you sure?\n\nType `CONFIRM` to confirm"
    timeOutText = "Build request timed out"
    cancelMsg = "Build request cancelled."
    if not await warnUser(ctx, client, warnText, cancelMsg, timeOutText, 30, "CONFIRM"):
        return
    townData["PLOTS"][plot]["PLOTTYPE"] = structure
    playerData["BALANCE"] -= structurePrice
    if structure in [mineText, forestText, farmText, pondText]:
        playerData[structure + "S"] += 1
    setTownData(townID, townData)
    setPlayerData(ctx.author.id, playerData)
    embed.color = discord.Color.green()
    embed.description = f"{structure.capitalize()} built!"
    await ctx.send(embed=embed)
    return


async def clearHandler(ctx, plot):
    if not await isInTown(ctx):
        return
    plot = plot.upper()
    embed = makeEmbed()
    embed.color = discord.Color.red()
    townID = getPlayerTown(ctx.author.id)
    if not plotIsValid(plot):
        embed.description = "Invalid syntax! Syntax is `-plot clear YX`, i.e. `-plot clear C4`."
        await ctx.send(embed=embed)
        return
    townData = getTownData(townID)
    if not userOwnsPlot(ctx.author.id, townData, plot):
        embed.description = "You don't own that plot!"
        await ctx.send(embed=embed)
        return
    currentStructure = townData["PLOTS"][plot]["PLOTTYPE"]
    if currentStructure not in [mineText, forestText, farmText, pondText, houseText]:
        embed.description = "This plot is already cleared!"
        await ctx.send(embed=embed)
        return
    playerID = str(ctx.author.id)
    if currentStructure == houseText and countHousesOwned(playerID) <= 1:
        embed.description = "You cannot clear your only house!"
        await ctx.send(embed=embed)
        return
    townData["PLOTS"][plot]["PLOTTYPE"] = plainText
    playerData = getPlayerData(playerID)
    if currentStructure in [mineText, forestText, farmText, pondText]:
        playerData[currentStructure + "S"] -= 1
    setPlayerData(playerID, playerData)
    setTownData(townID, townData)
    embed.description = "Plot cleared!"
    embed.color = discord.Color.green()
    await ctx.send(embed=embed)


async def forsaleHandler(ctx, plot):
    playerID = str(ctx.author.id)
    if not await isInTown(ctx):
        return
    plot = plot.upper()
    embed = makeEmbed()
    embed.color = discord.Color.red()
    if not isMayor(playerID):
        embed.description = "Only the mayor can mark plots for sale! You can unclaim plots with `-plot unclaim YX`"
        await ctx.send(embed=embed)
        return
    if not plotIsValid(plot):
        embed.description = "Invalid syntax! Syntax is `-plot forsale YX`, i.e. `-plot forsale C4`."
        await ctx.send(embed=embed)
        return

    townID = getPlayerTown(playerID)
    townData = getTownData(townID)
    if not userOwnsPlot(playerID, townData, plot):
        embed.description = "You do not own that plot!"
        await ctx.send(embed=embed)
        return
    plotType = townData["PLOTS"][plot]["PLOTTYPE"]
    if plotType not in ["PLAIN", "HOUSE"]:
        embed.description = f"There is a structure on that plot! Use `-plot clear {plot}` first!"
        await ctx.send(embed=embed)
        return
    if plotType == houseText:
        if countHousesOwned(playerID) <= 1:
            embed.description = f"You can't sell your only house!"
            await ctx.send(embed=embed)
            return
        townData["PLOTS"][plot]["PLOTTYPE"] = "HOUSEFORSALE"
    else:
        townData["PLOTS"][plot]["PLOTTYPE"] = "FORSALE"
    townData["PLOTS"][plot]["OWNER"] = None

    setTownData(townID, townData)
    embed.description = f"Plot marked for sale!"
    embed.color = discord.Color.green()
    await ctx.send(embed=embed)
    return


async def notforsaleHandler(ctx, plot):
    playerID = str(ctx.author.id)
    if not await isInTown(ctx):
        return
    plot = plot.upper()
    embed = makeEmbed()
    embed.color = discord.Color.red()
    if not isMayor(playerID):
        embed.description = "Only the mayor can mark plots not for sale."
        await ctx.send(embed=embed)
        return
    if not plotIsValid(plot):
        embed.description = "Invalid syntax! Syntax is `-plot forsale YX`, i.e. `-plot forsale C4`."
        await ctx.send(embed=embed)
        return
    townID = getPlayerTown(playerID)
    townData = getTownData(townID)
    plotType = townData["PLOTS"][plot]["PLOTTYPE"]
    if plotType not in [forsaleText, houseforsaleText]:
        embed.description = "This plot is already not for sale."
        await ctx.send(embed=embed)
        return
    townData["PLOTS"][plot]["OWNER"] = playerID
    if plotType == forsaleText:
        townData["PLOTS"][plot]["PLOTTYPE"] = plainText
    else:
        townData["PLOTS"][plot]["PLOTTYPE"] = houseText
    setTownData(townID, townData)
    embed.description = f"Plot marked not for sale!"
    embed.color = discord.Color.green()
    await ctx.send(embed=embed)
    return


async def buyHandler(ctx, plot):
    playerID = str(ctx.author.id)
    if not await isInTown(ctx):
        return
    plot = plot.upper()
    embed = makeEmbed()
    if not plotIsValid(plot):
        embed.description = "Invalid syntax! Syntax is `-plot buy YX`, i.e. `-plot buy C4`."
        await ctx.send(embed=embed)
        return
    townID = getPlayerTown(playerID)
    townData = getTownData(townID)
    plotType = townData["PLOTS"][plot]["PLOTTYPE"]
    if plotType not in [forsaleText, houseforsaleText]:
        embed.description = "This plot is not for sale!"
        await ctx.send(embed=embed)
        return
    plotPrice = townData["PLOTPRICE"]
    playerData = getPlayerData(playerID)
    if playerData["BALANCE"] < plotPrice:
        embed.description = f"You cannot afford to buy this plot! Plots cost **${plotPrice}** in this town."
        await ctx.send(embed=embed)
        return
    townData["PLOTS"][plot]["OWNER"] = playerID
    if plotType == forsaleText:
        townData["PLOTS"][plot]["PLOTTYPE"] = plainText
    else:
        townData["PLOTS"][plot]["PLOTTYPE"] = houseText
    setTownData(townID, townData)
    mayorID = townData["MAYOR"]
    mayorData = getPlayerData(mayorID)
    mayorData["BALANCE"] += plotPrice
    setPlayerData(mayorID, mayorData)
    playerData["BALANCE"] -= plotPrice
    playerData["PLOTS"] += 1
    setPlayerData(playerID, playerData)
    embed.description = f"You now own this plot! You paid **${plotPrice}** for this plot."
    embed.color = discord.Color.green()
    await ctx.send(embed=embed)
    return


async def unclaimHandler(ctx, plot):
    playerID = str(ctx.author.id)
    if not await isInTown(ctx):
        return
    plot = plot.upper()
    embed = makeEmbed()
    if not plotIsValid(plot):
        embed.description = "Invalid syntax! Syntax is `-plot unclaim YX`, i.e. `-plot unclaim C4`."
        await ctx.send(embed=embed)
        return
    townID = getPlayerTown(playerID)
    townData = getTownData(townID)
    if not userOwnsPlot(playerID, townData, plot):
        embed.description = "You do not own that plot!"
        await ctx.send(embed=embed)
        return
    structureType = townData["PLOTS"][plot]["PLOTTYPE"]
    if structureType == houseText and countHousesOwned(playerID) <= 1:
        embed.description = "You cannot unclaim your only house!"
        await ctx.send(embed=embed)
        return
    if isMayor(playerID):
        embed.description = "You own the town, so you can't unclaim your own plots! You can remove plots from your town with `-plot abandon YX`."
        await ctx.send(embed=embed)
        return
    playerData = getPlayerData(playerID)
    if structureType in ["MINE", "FOREST", "FARM", "POND"]:
        playerData[structureType + "S"] -= 1
    playerData["PLOTS"] -= 1
    setPlayerData(playerID, playerData)
    mayorID = townData["MAYOR"]
    townData["PLOTS"][plot]["OWNER"] = mayorID
    if structureType != houseText:
        townData["PLOTS"][plot]["PLOTTYPE"] = plainText
    setTownData(townID, townData)
    embed.description = "Plot unclaimed!"
    await ctx.send(embed=embed)
    return

