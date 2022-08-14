import math
import random
import time

import discord
import secrets

from tbLib.playerData import *
from tbLib.tbutils import makeEmbed
from tbLib.nameGenerator import generateName
from tbLib.townsData import *
from tbLib.makeMap import makeOwnerMap, getMap
from tbLib.identifier import identify, getFullName
from tbLib.plots import makePlot, calculateNextPlot
from tbLib.tbutils import warnUser, isNumInLimits

townCost = 25000                                                                            # cost to make a town
plainText = "PLAIN"                                                                         # texts for JSON values, done to avoid typing mistakes
mineTest = "MINE"
forestText = "FOREST"
farmText = "FARM"
pondText = "POND"
houseText = "HOUSE"
forsaleText = "FORSALE"
houseforsaleText = "HOUSEFORSALE"


async def townsHelp(ctx):                                                                   # function called by -town, currently set to equivalent of -town info
    await townInfoHandler(ctx)


async def townInfoHandler(ctx, name="NONE"):                                                # handles providing information from the town
    embed = makeEmbed()
    embed.color = discord.Color.red()
    if name == "NONE":                                                                      # if no town argument is specified, retrieves the ID of the player's town
        townID = getPlayerTown(ctx.author.id)
        if townID is None:                                                                  # if the player is not in a town, throw an error
            embed.description = "You are not in a town!"
            await ctx.send(embed=embed)
            return
    else:
        townID = findTownID(name)                                                           # retrieves the ID of the town specified if the player specifies it
        if townID is None:
            embed = makeEmbed()
            embed.description = "That town does not exist!"
            await ctx.send(embed=embed)
            return
    townData = getTownData(townID)                                                          # gets town info
    townName = townData["NAME"]
    townMayor = townData["MAYOR"]
    plotPrice = townData["PLOTPRICE"]
    townSize = len(townData["PLOTS"])
    residents = []
    for resident in townData["RESIDENTS"]:
        residents.append("**" + getPlayerData(resident)["NAME"] + "**")                     # gets the name of the residents
    embed.color = discord.Color.purple()
    # provide town name, mayor, amount of plots in the town, the residents in the server, the price to buy a plot,
    # and the price to annex a plot.
    embed.description = f"""Information for **{townName}**:\n\nMayor: **{getFullName(townMayor)}**\n
                            Amount of plots: **{townSize}**\n\nResidents: {str(residents)[1:-1].replace("'", "")}\n
                            \nPrice to own a plot: **${plotPrice}**\nPrice to annex a plot: **${calculateNextPlot(townSize)}**
                            \n\nDo `-town map {townName}` to see a map of this town!"""
    await ctx.send(embed=embed)


async def newTownHandler(ctx, client, name="NONE"):                                         # handles creating a new town
    playerID = str(ctx.author.id)
    playerData = getPlayerData(playerID)
    embed = makeEmbed()
    embed.color = discord.Color.red()
    if not playerData["TOWN"] is None:                                                      # checks if the user is already in a town
        embed.description = "You are already in a town!"
        await ctx.send(embed=embed)
        return
    if playerData["BALANCE"] < townCost:                                                    # checks if the user can afford making a new town
        embed.description = f"You cannot afford a town! Towns cost ${townCost}."
        await ctx.send(embed=embed)
        return
    townID = secrets.token_hex(16)                                                          # creates a 16 byte hex ID for towns
    if name == "NONE":                                                                      # if a name is not given, the name is generated using nameGenerator
        name = generateName()
    if not findTownID(name) is None:                                                        # checks if there is already a town with that name
        embed.description = f"There is already a town with this name!"
        await ctx.send(embed=embed)
        return
    townName = name
    warnText = f"""Are you sure you want to create a town? It will cost **${townCost}**.
                \n\nType `CONFIRM` to confirm."""
    timeOutText = "Town deletion request timed out."
    cancelMsg = "Town deletion request cancelled."
    # warns the user how much the town will cost, and waits for the user to confirm
    if not await warnUser(ctx, client, warnText, cancelMsg, timeOutText, 30, "CONFIRM"):
        return
    with open(f"non-code/inittown.json", "r") as read_file:                                 # gets init data for a town
        townData = json.load(read_file)
    townData["NAME"] = townName                                                             # sets needed data for the town
    townData["MAYOR"] = playerID
    starterPlots = ["E4", "E5", "F4", "F5"]                                                 # towns start with 4 plots
    for plot in starterPlots:
        townData["PLOTS"][plot] = makePlot(playerID, plainText)                             # initialize the 4 plots
    housePlot = random.choice(starterPlots)                                                 # there will be a house on a random plot
    townData["PLOTS"][housePlot] = makePlot(playerID, houseText)                            # initialize the rest of the needed data
    townData["RESIDENTS"].append(playerID)
    townData["TIMEMADE"] = int(time.time())                                                 # time made used for -town list ordering
    setTownData(townID, townData)
    playerData["BALANCE"] -= townCost                                                       # set player data
    playerData["TOWN"] = townID
    playerData["PLOTS"] += 4
    setPlayerData(playerID, playerData)
    embed.description = f"**__NEW TOWN MADE__**\n Your new town name is {townName}!"
    embed.color = discord.Color.green()
    await ctx.send(embed=embed)


async def deleteTownHandler(ctx, client):                                                   # handles deleting a town
    embed = makeEmbed()
    userID = str(ctx.author.id)
    if not isMayor(userID):                                                                 # checks if the player is the mayor of a town
        embed.description = "You do not own a town!"
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return
    warnText = """Are you sure you want to delete your town? Your plots and your resident's plots will be gone forever!\n\nType `DELETE` to confirm"""
    timeOutText = "Town deletion request timed out."
    cancelMsg = "Town deletion request cancelled."
    # warns the user of what happens when the town is deleted, and waits for user to confirm
    if not await warnUser(ctx, client, warnText, cancelMsg, timeOutText, 30, "DELETE"):
        return
    townID = getPlayerData(ctx.author.id)["TOWN"]
    townName = getTownName(townID)
    evicted = getTownData(townID)["RESIDENTS"]
    for user in evicted:                                                                    # goes through every resident and resets their data
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
    for user in evicted:                                                                    # lists every user who was in the town
        embed.description += getFullName(user) + "\n"
    await ctx.send(embed=embed)


async def renameHandler(ctx, name):                                                         # handles renaming a town
    embed = makeEmbed()
    if not isMayor:                                                                         # checks if the user is a mayor
        embed.description = "You don't own a town!"
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return
    if not findTownID(name) is None:                                                        # checks if there is already a town with that name
        embed.description = f"There is already a town with this name!"
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


async def makeMapHandler(ctx, town="NONE"):                                                 # handles making maps by calling the map creator
    if not await canMakeMap(ctx):                                                           # checks if the user's timer for making a map has expired
        return
    townFile = await getMap(ctx, town, "MAP")                                               # calls the map maker to make the map
    if townFile is None:
        return
    await ctx.send(file=discord.File(townFile))                                             # sends the map file
    os.remove(str(townFile))                                                                # deletes the map fil to make space


async def makeForSaleMapHandler(ctx, town="NONE"):                                          # handles making for sale maps
    if not await canMakeMap(ctx):                                                           # identical logic to makeMapHandler
        return
    townFile = await getMap(ctx, town, "FORSALE")
    if townFile is None:
        return
    await ctx.send(file=discord.File(townFile))
    os.remove(str(townFile))


async def leaveHandler(ctx, client):                                                        # handles players leaving a town
    embed = makeEmbed()
    embed.color = discord.Color.red()
    playerID = str(ctx.author.id)
    townID = getPlayerTown(playerID)
    if townID is None:                                                                      # checks if the user is in a town
        embed.description = "You are already not in a town!"
        await ctx.send(embed=embed)
        return
    if isMayor(playerID):                                                                   # checks if user is a mayor, since mayors cannot leave
        embed.description = "You cannot leave a town you own! Appoint another mayor using `-town set mayor <new mayor>` or delete the town using `-town delete`."
        await ctx.send(embed=embed)
        return
    warnText = """Are you sure you want to leave your town? Your plots will be gone forever!
                \n\nType `CONFIRM` to confirm"""
    timeOutText = "Town leave request timed out."
    cancelMsg = "Town leave request cancelled."
    # warns the user of what happens when they leave a town, and waits until user confirms
    if not await warnUser(ctx, client, warnText, cancelMsg, timeOutText, 30, "CONFIRM"):
        return
    clearUserLand(playerID)
    embed.description = "You left town."
    await ctx.send(embed=embed)


async def kickHandler(ctx, client, resident):                                               # handles kicking players from town
    embed = makeEmbed()
    embed.color = discord.Color.red()
    mayorID = str(ctx.author.id)
    if not isMayor(mayorID):                                                                # checks if user is a mayor, only mayors can kick users
        embed.description = "You do not own a town!"
        await ctx.send(embed=embed)
        return
    residentID = identify(resident)
    if residentID.startswith("ERROR"):                                                      # if residentID starts with error, then the user doesnt exist
        embed.description = residentID.replace("ERROR ", "")                                # residentID is replaced with the error message, so print that
        await ctx.send(embed=embed)
        return
    townID = getPlayerTown(mayorID)
    townData = getTownData(townID)
    if residentID not in townData["RESIDENTS"]:                                             # checks if the user specified is actually in the town
        embed.description = f"**{getFullName(residentID)}** is not in your town!"
        await ctx.send(embed=embed)
        return
    warnText = f"""Are you sure you want to kick **{getFullName(residentID)}**? They will lose all their plots and structures!
                    \n\nType `CONFIRM` to confirm\n\nWARNING: Their plots will all be wiped"""
    timeOutText = "Town leave request timed out."
    cancelMsg = "Town leave request cancelled."
    # warns user of what happens when they kick a player, then waits for user to confirm
    if not await warnUser(ctx, client, warnText, cancelMsg, timeOutText, 30, "CONFIRM"):
        return
    clearUserLand(residentID)
    embed.description = f"**{getFullName(residentID)}** was kicked."
    await ctx.send(embed=embed)


def clearUserLand(playerID):                                                                # given a user, clears all town data
    playerData = getPlayerData(playerID)
    playerData["TOWN"] = None
    playerData["PLOTS"] = 0
    playerData["MINES"] = 0
    playerData["FORESTS"] = 0
    playerData["FARMS"] = 0
    playerData["PONDS"] = 0
    townID = getPlayerTown(playerID)
    townData = getTownData(townID)
    mayorID = townData["MAYOR"]                                                             # gets mayor ID to give plot to mayor
    mayorData = getPlayerData(mayorID)
    townData["RESIDENTS"].remove(playerID)
    for plot in townData["PLOTS"]:                                                          # iterates through every plot in the town
        if townData["PLOTS"][plot]["OWNER"] == playerID:                                    # checks if the plot is owned by the resident being cleared
            plotInfo = townData["PLOTS"][plot]
            plotInfo["OWNER"] = mayorID                                                     # sets the owner to the mayor
            mayorData["PLOTS"] += 1                                                         # increases mayor's plot count by 1
            if plotInfo["PLOTTYPE"] not in [houseText, plainText]:
                plotInfo["PLOTTYPE"] = plainText                                            # resets the plot if structures were on it
            townData["PLOTS"][plot] = plotInfo
    setTownData(townID, townData)
    setPlayerData(playerID, playerData)
    setPlayerData(mayorID, mayorData)


async def plotPriceHandler(ctx, value):                                                     # handles setting the price of plots
    embed = makeEmbed()
    embed.color = discord.Color.red()
    playerID = str(ctx.author.id)
    if not isMayor(playerID):                                                               # checks if the user owns the town, only mayors can set plot price
        embed.description = "You need to own a town to change the plot price!"
        await ctx.send(embed=embed)
        return
    valueCheck = isNumInLimits(value, 0, 1000000)                                           # checks if the value given is a valid number within limits
    if valueCheck == "NaN":                                                                 # number isnt a number
        embed.description = "Invalid syntax! Syntax is `-town set plotprice <number>`."
        await ctx.send(embed=embed)
        return
    if valueCheck == "LOW":                                                                 # number is below 0
        embed.description = "Plot price must be at least **$0**."
        await ctx.send(embed=embed)
        return
    if valueCheck == "HIGH":                                                                # number is above 1 million
        embed.description = "Plot price must be at most **$1,000,000**."
        await ctx.send(embed=embed)
        return
    townID = getPlayerTown(playerID)
    townData = getTownData(townID)
    townData["PLOTPRICE"] = int(value)
    setTownData(townID, townData)
    embed.color = discord.Color.green()
    embed.description = f"Plots now cost **${value}** to buy."
    await ctx.send(embed=embed)


async def newMayorHandler(ctx, newMayor, client):                                           # handles setting the new mayor of the town
    embed = makeEmbed()
    embed.color = discord.Color.red()
    playerID = str(ctx.author.id)
    if not isMayor(playerID):                                                               # checks if user is the mayor, only mayors can appoint a new mayor
        embed.description = "You need to own a town to change the plot price!"
        await ctx.send(embed=embed)
        return
    newMayorID = identify(newMayor)                                                         # finds the ID of the user mentioned
    if newMayorID.startswith("ERROR"):                                                      # if the ID starts with ERROR, user doesn't exist
        embed.description = newMayorID.replace("ERROR ", "")                                # mayorID is replaced with error message, so print that
        await ctx.send(embed=embed)
        return
    townID = getPlayerTown(playerID)
    townData = getTownData(townID)
    if newMayorID not in townData["RESIDENTS"]:                                             # checks if the new mayor is actually in the town
        embed.description = f"{getFullName(newMayorID)} is not in your town!"
        await ctx.send(embed=embed)
        return
    warnText = f"""Are you sure you want to give this town to **{getFullName(newMayorID)}**?
                \n\nType `CONFIRM` to confirm."""
    timeOutText = "Town set mayor request timed out."
    cancelMsg = "Town set mayor request cancelled."
    # warns the user and waits for confirmation
    if not await warnUser(ctx, client, warnText, cancelMsg, timeOutText, 30, "CONFIRM"):
        return
    townData["MAYOR"] = newMayorID                                                          # sets the mayor to the new mayor
    setTownData(townID, townData)
    embed.color = discord.Color.green()
    embed.description = f"**{getFullName(newMayorID)}** is now the new mayor!"
    await ctx.send(embed=embed)


async def makeOwnerMapHandler(ctx, resident="NONE"):                                        # handles making a map for plots a user owns
    if not await canMakeMap(ctx):
        return
    if resident == "NONE":                                                                  # if no user is specified, gets own user's map
        residentID = str(ctx.author.id)
    else:
        residentID = identify(resident)                                                     # identifies resident
        if residentID.startswith("ERROR"):                                                  # if residentID starts with ERROR, then resident doesnt exist
            embed = makeEmbed()
            embed.description = residentID.replace("ERROR ", "")                            # residentID is replaced with error message, so print that
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
    townID = getPlayerTown(residentID)
    if townID is None:                                                                      # checks if user is in a town
        embed = makeEmbed()
        embed.description = "This person is not in a town!"
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return
    townFile = makeOwnerMap(townID, residentID)                                             # calls makeOwnerMap
    await ctx.send(file=discord.File(townFile))                                             # sends map
    os.remove(townFile)                                                                     # deletes file to save space


async def canMakeMap(ctx):                                                                  # checks if player can make a map
    mapTimer = 3                                                                            # specifies how long a player has to wait between making maps
    playerData = getPlayerData(ctx.author.id)
    lastMap = int(time.time()) - playerData["LASTMAP"]                                      # calculates how much time it has been since the last map was made by the user
    if lastMap < mapTimer:                                                                  # if the time since last map is less than the required wait limit, throw error
        embed = makeEmbed()
        embed.color = discord.Color.red()
        embed.description = f"You must wait {mapTimer - lastMap} more seconds to make a map."   # let user know how much more time to wait
        await ctx.send(embed=embed)
        return False
    playerData["LASTMAP"] = int(time.time())                                                # otherwise, reset map timer and allow user to make the map
    setPlayerData(ctx.author.id, playerData)
    return True


async def townListHandler(ctx, page=1):                                                     # handles making a list of all towns
    embed = makeEmbed()
    valueCheck = isNumInLimits(page, 1, math.inf)                                           # checks if page given is a number within limits
    if valueCheck == "NaN":                                                                 # if number is not a number
        embed.description = "Invalid syntax! Syntax is `-town list <page>`."
        await ctx.send(embed=embed)
        return
    if valueCheck == "LOW":                                                                 # if number is below 1
        embed.description = "page must be at least **1**."
        await ctx.send(embed=embed)
        return
    towns = {}                                                                              # makes empty dictionary for simplified towns info
    for town in os.listdir("towns"):
        townID = town.replace(".json", "")
        townData = getTownData(townID)
        townName = townData["NAME"]
        timeMade = townData["TIMEMADE"]
        towns[townName] = timeMade                                                          # enters townName key with timeMade value, for ordering
    sortedTowns = sorted(towns.items(), key=lambda x: x[1])                                 # sorts dictionary by value
    embed.description = "**__Towns List:__**\n"
    place = 0                                                                               # keeps track of where in the sorted list the code is at
    pageSize = 10                                                                           # determines how many entries can fit on one page
    startPlace = (int(page) - 1) * pageSize                                                 # determines what place the printed page starts at
    leaderboard = []                                                                        # empty list for towns to be printed
    for town in sortedTowns:                                                                # goes through each town in the sorted list
        if startPlace <= place < startPlace + pageSize:                                     # if town place is within page limits, append to list
            townStats = f"{place + 1}. **{town[0]}**"                                       # prints place, then town name
            leaderboard.append(townStats)
        place += 1
    for town in leaderboard:                                                                # goes through every town in leaderboard to print
        embed.description += "\n" + town
    embed.color = discord.Color.purple()
    await ctx.send(embed=embed)

