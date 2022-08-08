from PIL import Image, ImageEnhance
import json
import random
import discord
from tbLib.playerData import *
from tbLib.townsData import *
from tbLib.makeEmbed import makeEmbed


async def getMap(ctx, arg, mapType):
    if arg == "NONE":
        townID = getPlayerTown(ctx.author.id)
    else:
        townID = findTownID(arg)
    if townID is None:
        embed = makeEmbed()
        embed.description = "This town doesn't exist!"
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return None
    if mapType == "MAP":
        townFile = makeMap(townID)
    else:
        townFile = makeForSaleMap(townID)
    return townFile


def makeMap(townID):
    townMap = Image.open("images/layout.png")
    with open(f"towns/{townID}.json", "r") as readFile:
        townData = json.load(readFile)
    for y in range(10):
        for x in range(10):
            offset = (64 * (x + 1), 64 * (y + 1))
            removeColor = False
            tileID = chr(y + 65) + str(x)
            tileName = getTile(townData, tileID)
            if tileID not in townData["PLOTS"]:
                removeColor = True
            tile = Image.open(f"images/{tileName}.png")
            if removeColor:
                tile = tile.convert("L")
            townMap.paste(tile, offset)
    fileName = f"images/maps/{townID}.png"
    townMap.save(fileName)
    return fileName


def makeOwnerMap(townID, resident):
    ownerMap = Image.open("images/layout.png")
    with open(f"towns/{townID}.json", "r") as readFile:
        townData = json.load(readFile)
    for y in range(10):
        for x in range(10):
            offset = (64 * (x + 1), 64 * (y + 1))
            removeColor = False
            darken = False
            tileID = chr(y + 65) + str(x)
            tileName = getTile(townData, tileID)
            if tileID not in townData["PLOTS"]:
                removeColor = True
            elif townData["PLOTS"][tileID]["OWNER"] != resident:
                darken = True
            tile = Image.open(f"images/{tileName}.png")
            if removeColor:
                tile = tile.convert("L")
            if darken:
                tile = ImageEnhance.Brightness(tile).enhance(0.5)
            ownerMap.paste(tile, offset)
    fileName = f"images/maps/{townID}{resident}.png"
    ownerMap.save(fileName)
    return fileName


def makeForSaleMap(townID):
    ownerMap = Image.open("images/layout.png")
    with open(f"towns/{townID}.json", "r") as readFile:
        townData = json.load(readFile)
    for y in range(10):
        for x in range(10):
            offset = (64 * (x + 1), 64 * (y + 1))
            removeColor = False
            darken = False
            tileID = chr(y + 65) + str(x)
            tileName = getTile(townData, tileID)
            if tileID not in townData["PLOTS"]:
                removeColor = True
            elif tileName not in ["forsale", "houseforsale"]:
                darken = True
            tile = Image.open(f"images/{tileName}.png")
            if removeColor:
                tile = tile.convert("L")
            if darken:
                tile = ImageEnhance.Brightness(tile).enhance(0.5)
            ownerMap.paste(tile, offset)
    fileName = f"images/maps/{townID}forsale.png"
    ownerMap.save(fileName)
    return fileName


def getTile(townData, tileID):
    tileTypes = {
        "PLAIN": ["plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain3", "plain3", "plain3", "plain2", "plain1"],
        "MINE": ["mine1", "mine2"],
        "FOREST": ["forest1", "forest2"],
        "FARM": ["farm1", "farm2"],
        "POND": ["pond1", "pond2", "pond3"],
        "HOUSE": ["house"],
        "FORSALE": ["forsale"],
        "HOUSEFORSALE": ["houseforsale"]
    }
    if tileID not in townData["PLOTS"]:
        return random.choice(tileTypes["PLAIN"])
    return random.choice(tileTypes[townData["PLOTS"][tileID]["PLOTTYPE"]])
