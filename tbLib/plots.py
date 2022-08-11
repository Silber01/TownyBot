import discord

from tbLib.playerData import *
from tbLib.townsData import *
from tbLib.identifier import *
from tbLib.tbutils import warnUser, makeEmbed
from tbLib.validPlotDelete import canRemovePlot

houseCost = 1000                                                        # price to buy a house
plainText = "PLAIN"                                                     # structure values that the JSON save data uses
mineText = "MINE"
forestText = "FOREST"
farmText = "FARM"
pondText = "POND"
houseText = "HOUSE"
forsaleText = "FORSALE"
houseforsaleText = "HOUSEFORSALE"


#goes through player's town and counts how many of the plots are houses and are owned by the player
def countHousesOwned(playerID):
    townID = getPlayerTown(playerID)
    townData = getTownData(townID)
    houseCount = 0
    for plot in townData["PLOTS"]:
        plotData = townData["PLOTS"][plot]
        if str(plotData["OWNER"]) == playerID and plotData["PLOTTYPE"] == houseText:
            houseCount += 1
    return houseCount


async def isInTown(ctx):                                                # checks if a player is in a town
    townID = getPlayerTown(ctx.author.id)
    if townID is None:                                                  # getPlayerTown returns none if not in a town
        embed = makeEmbed()                                             # lets player know they are not in a town
        embed.description = "You are not in a town!"
        await ctx.send(embed=embed)
        return False
    return True                                                         # returns true if town is not None


def calculateNextPlot(plotsOwned):                                      # returns how much it will cost to annex another plot
    return 250 * plotsOwned


def calculateNextStructurePrice(playerData, plottype):                  # returns how much it will cost to create another structure
    plottype = plottype.upper()
    if plottype not in [mineText, forestText, farmText, pondText]:
        return -1
    plotCount = playerData[plottype + "S"]                              # + S to convert to plural form, i.e. MINE becomes MINES, etc.
    return int(100 * (2 ** (plotCount + 2)))                            # required price goes up exponentially


def makePlot(owner, plottype=plainText):                                # shortcut for making a plot with proper information
    return {"OWNER": owner, "PLOTTYPE": plottype}


def plotIsValid(plot):                                                  # checks if a given plot argument is valid
    if len(plot) != 2:
        return False
    if not 65 <= ord(plot[0]) <= 74:                                    # Y coordinate between A and J
        return False
    if not 48 <= ord(plot[1]) <= 57:                                    # X coordinate between 0 and 9
        return False
    return True


def userOwnsPlot(userID, townData, plot):                               # given a plot and player, returns whether they own the plot
    if plot not in townData["PLOTS"]:                                   # trivial case for if the plot does not exist
        return False
    return townData["PLOTS"][plot]["OWNER"] == str(userID)


def structureIsValid(structure):                                        # checks if a given structure argument is valid
    if structure in [mineText, forestText, farmText, pondText, houseText]:
        return True
    return False


# gives information for a given plot for the town the player is in, including owner and structure type
async def plotInfo(ctx, plot):
    if not await isInTown(ctx):                                         # checks if the player is in a town
        return
    plot = plot.upper()                                                 # formats plot data
    embed = makeEmbed()                                                 # prepares embed
    townID = getPlayerTown(ctx.author.id)
    if not plotIsValid(plot):                                           # checks if given plot is a valid input
        embed.color = discord.Color.red()
        embed.description = "Invalid syntax! Syntax is `-plot info YX`, i.e. `-plot info C4`."
        await ctx.send(embed=embed)
        return
    townData = getTownData(townID)
    plotsData = townData["PLOTS"]
    if plot not in plotsData:                                           # checks if the plot is part of the town
        embed.color = discord.Color.dark_gray()
        embed.description = "This plot is unclaimed."
        await ctx.send(embed=embed)
        return
    townName = townData["NAME"]
    plotType = plotsData[plot]["PLOTTYPE"]
    if plotsData[plot]["OWNER"] is None:                                # edge case for if the plot is for sale (in which case nobody owns it)
        embed.color = discord.Color.dark_gray()
        embed.description = "This plot is for sale."
        await ctx.send(embed=embed)
        return
    owner = getFullName(plotsData[plot]["OWNER"])                       # prepares data to display for stats
    embed.color = discord.Color.purple()
    embed.description = f"Plot **{plot}** in **{townName}**:\n\nOwner: **{owner}**\nStructure: **{plotType.capitalize()}**"
    await ctx.send(embed=embed)


# uses bit manipulation to check the 4 cardinal directions, and check each of those for if they are part of the town
def isAdjacentToTown(plot, plotsData):
    plotY = ord(plot[0])
    plotX = ord(plot[1])
    adjacentPlots = [(chr(plotY + 1) + chr(plotX)), (chr(plotY - 1) + chr(plotX)),
                     (chr(plotY) + chr(plotX + 1)), (chr(plotY) + chr(plotX - 1))]
    for adjPlot in adjacentPlots:
        if adjPlot in plotsData:
            return True
    return False


# handles logic and data for annexing a plot
async def annexHandler(ctx, plot, client):
    if not await isInTown(ctx):                                         # checks if the player is in a town
        return
    plot = plot.upper()                                                 # formats plot data
    embed = makeEmbed()                                                 # prepares embed
    embed.color = discord.Color.red()
    townID = getPlayerTown(ctx.author.id)
    if not plotIsValid(plot):                                           # checks if the plot argument is valid
        embed.description = "Invalid syntax! Syntax is `-plot annex YX`, i.e. `-plot annex C4`."
        await ctx.send(embed=embed)
        return
    playerID = str(ctx.author.id)
    if not isMayor(playerID):                                           # checks if the player is the mayor
        embed.description = "Only the mayor can annex plots!"
        await ctx.send(embed=embed)
        return
    townData = getTownData(getPlayerTown(ctx.author.id))
    plotsData = townData["PLOTS"]
    if plot in plotsData:                                               # checks if the plot is already part of the town
        embed.description = "This plot already belongs to the town!"
        await ctx.send(embed=embed)
        return
    if not isAdjacentToTown(plot, plotsData):                           # checks if the plot is not adjacent to existing land
        embed.description = "This plot is not adjacent to the town!"
        await ctx.send(embed=embed)
        return
    annexCost = calculateNextPlot(len(plotsData))
    playerData = getPlayerData(ctx.author.id)
    if playerData["BALANCE"] < annexCost:                               # checks if the player can afford annexing a plot
        embed.description = f"You cannot afford this! A new plot will cost **${annexCost}**."
        await ctx.send(embed=embed)
        return
    warnText = f"This will cost **${annexCost}** to annex. Are you sure?\n\nType `CONFIRM` to confirm"
    timeOutText = "Annex request timed out"
    cancelMsg = "Annex request cancelled."
    # lets the user know how much it will cost to annex the plot, and asks the user to confirm that they agree to the price
    if not await warnUser(ctx, client, warnText, cancelMsg, timeOutText, 30, "CONFIRM"):
        return
    newPlot = makePlot(playerID)
    townData["PLOTS"][plot] = newPlot                                   # sets town and player data to accomodate new plot
    playerData["BALANCE"] -= annexCost
    playerData["PLOTS"] += 1
    setPlayerData(playerID, playerData)
    setTownData(townID, townData)
    embed.color = discord.Color.green()
    embed.description = "Plot annexed!"
    await ctx.send(embed=embed)
    return


# handles logic and save data for building structures on a plot
async def buildHandler(ctx, plot, structure, client):
    if not await isInTown(ctx):                                         # checks if the player is in a town
        return
    plot = plot.upper()                                                 # formats plot data
    embed = makeEmbed()                                                 # prepares embed
    embed.color = discord.Color.red()
    townID = getPlayerTown(ctx.author.id)
    if not plotIsValid(plot):                                           # checks if plot argument is valid
        embed.description = "Invalid syntax! Syntax is `-plot build <structure> YX`, i.e. `-plot build mine C4`."
        await ctx.send(embed=embed)
        return
    townData = getTownData(townID)
    if not userOwnsPlot(ctx.author.id, townData, plot):                 # checks if the user owns the plot
        embed.description = "You don't own that plot!"
        await ctx.send(embed=embed)
        return
    currentStructure = townData["PLOTS"][plot]["PLOTTYPE"]
    if currentStructure != plainText:                                   # checks if a structure is already on the plot
        embed.description = f"There is already a {currentStructure.lower()} on that plot!"
        await ctx.send(embed=embed)
        return
    structure = structure.upper()
    if not structureIsValid(structure):                                 # checks if structure argument is valid
        embed.description = "Invalid structure! Structures you can build are `mine`, `forest`, `farm`, and `pond`. Mayors can also build `house`."
        await ctx.send(embed=embed)
        return
    playerData = getPlayerData(ctx.author.id)
    if structure == houseText:
        if not isMayor(str(ctx.author.id)):                             # if the player is building a house, checks if they are a mayor
            embed.description = "You need to be a mayor to build a house!"
            await ctx.send(embed=embed)
            return
        structurePrice = 1000                                           # returns structure price for houses
    else:
        structurePrice = calculateNextStructurePrice(playerData, structure)  # returns structure price for work structures
    if playerData["BALANCE"] < structurePrice:                          # checks if the user can afford building the structure
        embed.description = f"You Cannot afford that! The price to build a new **{structure.lower()}** is **${structurePrice}**."
        await ctx.send(embed=embed)
        return
    warnText = f"This will cost **${structurePrice}** to build. Are you sure?\n\nType `CONFIRM` to confirm"
    timeOutText = "Build request timed out"
    cancelMsg = "Build request cancelled."
    # warns user how much it will cost to build the structure, and asks user to confirm action
    if not await warnUser(ctx, client, warnText, cancelMsg, timeOutText, 30, "CONFIRM"):
        return
    townData["PLOTS"][plot]["PLOTTYPE"] = structure                     # sets user and player data for building the structure
    playerData["BALANCE"] -= structurePrice
    if structure in [mineText, forestText, farmText, pondText]:
        playerData[structure + "S"] += 1                                # sets player structure count
    setTownData(townID, townData)
    setPlayerData(ctx.author.id, playerData)
    embed.color = discord.Color.green()
    embed.description = f"{structure.capitalize()} built!"
    await ctx.send(embed=embed)
    return


async def abandonHandler(ctx, client, plot):
    if not await isInTown(ctx):                                         # checks if the player is in a town
        return
    plot = plot.upper()                                                 # formats plot data
    embed = makeEmbed()                                                 # prepares embed
    embed.color = discord.Color.red()
    playerID = str(ctx.author.id)
    if not isMayor(playerID):                                           # checks if the user is the mayor
        embed.description = "Only the mayor can abandon plots!"
        await ctx.send(embed=embed)
        return
    if not plotIsValid(plot):                                           # checks if the plot argument is valid
        embed.description = "Invalid Syntax! Syntax is `-plot abandon YX` i.e. `-plot abandon C4`."
        await ctx.send(embed=embed)
        return
    townID = getPlayerTown(playerID)
    townData = getTownData(townID)
    if not userOwnsPlot(playerID, townData, plot):                      # checks if user owns the plot
        embed.description = "You need to own this plot in order to abandon it!"
        await ctx.send(embed=embed)
        return
    if townData["PLOTS"][plot]["PLOTTYPE"] != plainText:                # checks if the plot is plains (you cannot abandon plots with structures on it)
        embed.description = f"This plot needs to be clear before you abandon it! DO `-plot clear {plot}` first."
        await ctx.send(embed=embed)
        return
    if not canRemovePlot(townData["PLOTS"], plot):                      # checks if removing the plot will cause the town to split apart
        embed.description = f"Removing this plot will split the town apart! You can't do that!"
        await ctx.send(embed=embed)
        return
    warnText = f"Are you sure you want to remove this plot?\n\nType `CONFIRM` to confirm"
    timeOutText = "Abandon request timed out"
    cancelMsg = "Abandon request cancelled."
    # warns user that the plot is going to be removed, and waits for confirmation by user
    if not await warnUser(ctx, client, warnText, cancelMsg, timeOutText, 30, "CONFIRM"):
        return
    del townData["PLOTS"][plot]                                         # sets player and town information to accomodate abandoned plot
    setTownData(townID, townData)
    mayorData = getPlayerData(playerID)
    mayorData["PLOTS"] -= 1
    setPlayerData(playerID, mayorData)
    embed.color = embed.color.green()
    embed.description = "Plot abandoned."
    await ctx.send(embed=embed)


async def clearHandler(ctx, plot):
    if not await isInTown(ctx):                                         # checks if the player is in a town
        return
    plot = plot.upper()                                                 # formats plot data
    embed = makeEmbed()                                                 # prepares embed
    embed.color = discord.Color.red()
    townID = getPlayerTown(ctx.author.id)
    if not plotIsValid(plot):                                           # checks if plot argument is valid
        embed.description = "Invalid syntax! Syntax is `-plot clear YX`, i.e. `-plot clear C4`."
        await ctx.send(embed=embed)
        return
    townData = getTownData(townID)
    if not userOwnsPlot(ctx.author.id, townData, plot):                 # checks if user owns the plot in question
        embed.description = "You don't own that plot!"
        await ctx.send(embed=embed)
        return
    currentStructure = townData["PLOTS"][plot]["PLOTTYPE"]
    if currentStructure not in [mineText, forestText, farmText, pondText, houseText]:   #checks if there is actually a structure on the plot
        embed.description = "This plot is already cleared!"
        await ctx.send(embed=embed)
        return
    playerID = str(ctx.author.id)
    if currentStructure == houseText and countHousesOwned(playerID) <= 1:               # checks if the player is trying to clear their only house
        embed.description = "You cannot clear your only house!"
        await ctx.send(embed=embed)
        return
    townData["PLOTS"][plot]["PLOTTYPE"] = plainText                     # converts the plot to plains
    playerData = getPlayerData(playerID)
    if currentStructure in [mineText, forestText, farmText, pondText]:  # if the plot had a structure on it, reduces the amount of those structures owned by user
        playerData[currentStructure + "S"] -= 1
    setPlayerData(playerID, playerData)                                 # sets player data
    setTownData(townID, townData)                                       # sets town data
    embed.description = "Plot cleared!"
    embed.color = discord.Color.green()
    await ctx.send(embed=embed)


async def forsaleHandler(ctx, plot):
    playerID = str(ctx.author.id)
    if not await isInTown(ctx):                                         # checks if the player is in a town
        return
    plot = plot.upper()                                                 # formats plot data
    embed = makeEmbed()                                                 # prepares embed
    embed.color = discord.Color.red()
    if not isMayor(playerID):                                           # checks if the user is the mayor of the town
        embed.description = "Only the mayor can mark plots for sale! You can unclaim plots with `-plot unclaim YX`"
        await ctx.send(embed=embed)
        return
    if not plotIsValid(plot):                                           # checks if the plot argument is valid
        embed.description = "Invalid syntax! Syntax is `-plot forsale YX`, i.e. `-plot forsale C4`."
        await ctx.send(embed=embed)
        return
    townID = getPlayerTown(playerID)
    townData = getTownData(townID)
    if not userOwnsPlot(playerID, townData, plot):                      # checks if the user owns that plot
        embed.description = "You do not own that plot!"
        await ctx.send(embed=embed)
        return
    plotType = townData["PLOTS"][plot]["PLOTTYPE"]
    if plotType not in ["PLAIN", "HOUSE"]:                              # checks if the plot is plains or house, the only plots that are sellable
        embed.description = f"There is a structure on that plot! Use `-plot clear {plot}` first!"
        await ctx.send(embed=embed)
        return
    if plotType == houseText:                                           # checks if the plot is a house
        if countHousesOwned(playerID) <= 1:                             # checks if the plot is the user's only house
            embed.description = f"You can't sell your only house!"
            await ctx.send(embed=embed)
            return
        townData["PLOTS"][plot]["PLOTTYPE"] = "HOUSEFORSALE"            # sets plot type to houseforsale
    else:
        townData["PLOTS"][plot]["PLOTTYPE"] = "FORSALE"                 # sets plot type to forsale if not a house
    townData["PLOTS"][plot]["OWNER"] = None
    playerData = getPlayerData(playerID)                                # sets player and town data to accomodate for sale plot
    playerData["PLOTS"] -= 1
    setPlayerData(playerID, playerData)
    setTownData(townID, townData)
    embed.description = f"Plot marked for sale!"
    embed.color = discord.Color.green()
    await ctx.send(embed=embed)
    return


async def notforsaleHandler(ctx, plot):
    playerID = str(ctx.author.id)
    if not await isInTown(ctx):                                         # checks if the player is in a town
        return
    plot = plot.upper()                                                 # formats plot data
    embed = makeEmbed()                                                 # prepares embed
    embed.color = discord.Color.red()
    if not isMayor(playerID):                                           # checks if the player is the mayor
        embed.description = "Only the mayor can mark plots not for sale."
        await ctx.send(embed=embed)
        return
    if not plotIsValid(plot):                                           # checks if the plot argument is valid
        embed.description = "Invalid syntax! Syntax is `-plot forsale YX`, i.e. `-plot forsale C4`."
        await ctx.send(embed=embed)
        return
    townID = getPlayerTown(playerID)
    townData = getTownData(townID)
    plotType = townData["PLOTS"][plot]["PLOTTYPE"]
    if plotType not in [forsaleText, houseforsaleText]:                 # checks if the plot is for sale
        embed.description = "This plot is already not for sale."
        await ctx.send(embed=embed)
        return
    townData["PLOTS"][plot]["OWNER"] = playerID                         # gives the plot back to the mayor
    if plotType == forsaleText:                                         # returns the plot to the appropriate not for sale plot
        townData["PLOTS"][plot]["PLOTTYPE"] = plainText
    else:
        townData["PLOTS"][plot]["PLOTTYPE"] = houseText
    setTownData(townID, townData)                                       # sets town data
    embed.description = f"Plot marked not for sale!"
    embed.color = discord.Color.green()
    await ctx.send(embed=embed)
    playerData = getPlayerData(playerID)                                # increases the plot count of the mayor
    playerData["PLOTS"] += 1
    setPlayerData(playerID, playerData)
    return


async def buyHandler(ctx, plot):
    playerID = str(ctx.author.id)
    if not await isInTown(ctx):                                         # checks if the player is in a town
        return
    plot = plot.upper()                                                 # formats plot data
    embed = makeEmbed()                                                 # prepares embed
    if not plotIsValid(plot):                                           # checks if the plot argument is valid
        embed.description = "Invalid syntax! Syntax is `-plot buy YX`, i.e. `-plot buy C4`."
        await ctx.send(embed=embed)
        return
    townID = getPlayerTown(playerID)
    townData = getTownData(townID)
    plotType = townData["PLOTS"][plot]["PLOTTYPE"]
    if plotType not in [forsaleText, houseforsaleText]:                 # checks if the plot is either a plains for sale or a house for sale
        embed.description = "This plot is not for sale!"
        await ctx.send(embed=embed)
        return
    plotPrice = townData["PLOTPRICE"]
    playerData = getPlayerData(playerID)
    if playerData["BALANCE"] < plotPrice:                               # checks if player can afford buying the plot
        embed.description = f"You cannot afford to buy this plot! Plots cost **${plotPrice}** in this town."
        await ctx.send(embed=embed)
        return
    townData["PLOTS"][plot]["OWNER"] = playerID
    if plotType == forsaleText:                                         # converts from the for sale plots to the appropriate owned plot
        townData["PLOTS"][plot]["PLOTTYPE"] = plainText
    else:
        townData["PLOTS"][plot]["PLOTTYPE"] = houseText
    setTownData(townID, townData)                                       # sets town and player data to accomodate for the bought plot
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
    if not await isInTown(ctx):                                         # checks if the player is in a town
        return
    plot = plot.upper()                                                 # formats plot data
    embed = makeEmbed()                                                 # prepares embed
    if not plotIsValid(plot):                                           # checks if plot argument is valid
        embed.description = "Invalid syntax! Syntax is `-plot unclaim YX`, i.e. `-plot unclaim C4`."
        await ctx.send(embed=embed)
        return
    townID = getPlayerTown(playerID)
    townData = getTownData(townID)
    if not userOwnsPlot(playerID, townData, plot):                      # checks if user owns the plot in question
        embed.description = "You do not own that plot!"
        await ctx.send(embed=embed)
        return
    structureType = townData["PLOTS"][plot]["PLOTTYPE"]
    if structureType == houseText and countHousesOwned(playerID) <= 1:  # checks if the plot the user is trying to unclaim is their only house
        embed.description = "You cannot unclaim your only house!"
        await ctx.send(embed=embed)
        return
    if isMayor(playerID):                                               # checks if player is mayor
        embed.description = "You own the town, so you can't unclaim your own plots! You can remove plots from your town with `-plot abandon YX`."
        await ctx.send(embed=embed)
        return
    playerData = getPlayerData(playerID)
    if structureType in ["MINE", "FOREST", "FARM", "POND"]:             # checks if the plot had a structure on it, then removes it from player data
        playerData[structureType + "S"] -= 1
    playerData["PLOTS"] -= 1
    setPlayerData(playerID, playerData)
    mayorID = townData["MAYOR"]
    townData["PLOTS"][plot]["OWNER"] = mayorID                          # gives the plot to the mayor
    if structureType != houseText:                                      # all structures except houses get wiped
        townData["PLOTS"][plot]["PLOTTYPE"] = plainText
    setTownData(townID, townData)                                       # set town data
    embed.description = "Plot unclaimed!"
    await ctx.send(embed=embed)
    return
