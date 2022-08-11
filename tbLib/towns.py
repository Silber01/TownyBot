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
    await townInfoHandler(ctx)


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
    plotPrice = townData["PLOTPRICE"]
    townSize = len(townData["PLOTS"])
    residents = []
    for resident in townData["RESIDENTS"]:
        residents.append("**" + getPlayerData(resident)["NAME"] + "**")
    embed.color = discord.Color.purple()
    embed.description = f"""Information for **{townName}**:\n\nMayor: **{getFullName(townMayor)}**\n
                            Amount of plots: **{townSize}**\n\nResidents: {str(residents)[1:-1].replace("'", "")}\n
                            \nPrice to own a plot: **${plotPrice}**\nPrice to annex a plot: **${calculateNextPlot(townSize)}**
                            \n\nDo `-town map {townName}` to see a map of this town!"""
    await ctx.send(embed=embed)


async def newTownHandler(ctx, client, name="NONE"):
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
    townName = name
    warnText = f"""Are you sure you want to create a town? It will cost **${townCost}**.
                \n\nType `CONFIRM` to confirm."""
    timeOutText = "Town deletion request timed out."
    cancelMsg = "Town deletion request cancelled."
    if not await warnUser(ctx, client, warnText, cancelMsg, timeOutText, 30, "CONFIRM"):
        return
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
    townData["TIMEMADE"] = int(time.time())
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
    warnText = """Are you sure you want to delete your town? Your plots and your resident's plots will be gone forever!\n\nType `DELETE` to confirm"""
    timeOutText = "Town deletion request timed out."
    cancelMsg = "Town deletion request cancelled."
    if not await warnUser(ctx, client, warnText, cancelMsg, timeOutText, 30, "DELETE"):
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
    warnText = """Are you sure you want to leave your town? Your plots will be gone forever!
                \n\nType `CONFIRM` to confirm"""
    timeOutText = "Town leave request timed out."
    cancelMsg = "Town leave request cancelled."
    if not await warnUser(ctx, client, warnText, cancelMsg, timeOutText, 30, "CONFIRM"):
        return
    clearUserLand(playerID)
    embed.description = "You left town."
    await ctx.send(embed=embed)


async def kickHandler(ctx, client, resident):
    embed = makeEmbed()
    embed.color = discord.Color.red()
    mayorID = str(ctx.author.id)
    if not isMayor(mayorID):
        embed.description = "You do not own a town!"
        await ctx.send(embed=embed)
        return
    residentID = identify(resident)
    if residentID.startswith("ERROR"):
        embed.description = residentID.replace("ERROR ", "")
        await ctx.send(embed=embed)
        return
    townID = getPlayerTown(mayorID)
    townData = getTownData(townID)
    if residentID not in townData["RESIDENTS"]:
        embed.description = f"**{getFullName(residentID)}** is not in your town!"
        await ctx.send(embed=embed)
        return
    warnText = f"""Are you sure you want to kick **{getFullName(residentID)}**? They will lose all their plots and structures!
                    \n\nType `CONFIRM` to confirm\n\nWARNING: Their plots will all be wiped"""
    timeOutText = "Town leave request timed out."
    cancelMsg = "Town leave request cancelled."
    if not await warnUser(ctx, client, warnText, cancelMsg, timeOutText, 30, "CONFIRM"):
        return
    clearUserLand(residentID)
    embed.description = f"**{getFullName(residentID)}** was kicked."
    await ctx.send(embed=embed)


def clearUserLand(playerID):
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


async def plotPriceHandler(ctx, value):
    embed = makeEmbed()
    embed.color = discord.Color.red()
    playerID = str(ctx.author.id)
    if not isMayor(playerID):
        embed.description = "You need to own a town to change the plot price!"
        await ctx.send(embed=embed)
        return
    valueCheck = isNumInLimits(value, 0, 1000000)
    if valueCheck == "NaN":
        embed.description = "Invalid syntax! Syntax is `-town set plotprice <number>`."
        await ctx.send(embed=embed)
        return
    if valueCheck == "LOW":
        embed.description = "Plot price must be at least **$0**."
        await ctx.send(embed=embed)
        return
    if valueCheck == "HIGH":
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


async def newMayorHandler(ctx, newMayor, client):
    embed = makeEmbed()
    embed.color = discord.Color.red()
    playerID = str(ctx.author.id)
    if not isMayor(playerID):
        embed.description = "You need to own a town to change the plot price!"
        await ctx.send(embed=embed)
        return
    newMayorID = identify(newMayor)
    if newMayorID.startswith("ERROR"):
        embed.description = newMayorID.replace("ERROR ", "")
        await ctx.send(embed=embed)
        return
    townID = getPlayerTown(playerID)
    townData = getTownData(townID)
    if newMayorID not in townData["RESIDENTS"]:
        embed.description = f"{getFullName(newMayorID)} is not in your town!"
        await ctx.send(embed=embed)
        return
    warnText = f"""Are you sure you want to give this town to **{getFullName(newMayorID)}**?
                \n\nType `CONFIRM` to confirm."""
    timeOutText = "Town set mayor request timed out."
    cancelMsg = "Town set mayor request cancelled."
    if not await warnUser(ctx, client, warnText, cancelMsg, timeOutText, 30, "CONFIRM"):
        return
    townData["MAYOR"] = newMayorID
    setTownData(townID, townData)
    embed.color = discord.Color.green()
    embed.description = f"**{getFullName(newMayorID)}** is now the new mayor!"
    await ctx.send(embed=embed)



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


async def townListHandler(ctx, page=1):
    embed = makeEmbed()
    valueCheck = isNumInLimits(page, 1, math.inf)
    if valueCheck == "NaN":
        embed.description = "Invalid syntax! Syntax is `-town list <page>`."
        await ctx.send(embed=embed)
        return
    if valueCheck == "LOW":
        embed.description = "page must be at least **1**."
        await ctx.send(embed=embed)
        return
    towns = {}
    for town in os.listdir("towns"):
        townID = town.replace(".json", "")
        townData = getTownData(townID)
        townName = townData["NAME"]
        timeMade = townData["TIMEMADE"]
        towns[townName] = timeMade
    sortedTowns = sorted(towns.items(), key=lambda x: x[1])
    print(sortedTowns)
    embed = makeEmbed()
    embed.description = "**__Towns List:__**\n"
    place = 0
    pageSize = 10
    startPlace = (int(page) - 1) * pageSize
    leaderboard = []
    for town in sortedTowns:
        print(town[0])
        if startPlace <= place < startPlace + pageSize:
            townStats = f"{place + 1}. **{town[0]}**"
            leaderboard.append(townStats)
        place += 1
    for town in leaderboard:
        embed.description += "\n" + town
    embed.color = discord.Color.purple()
    await ctx.send(embed=embed)

