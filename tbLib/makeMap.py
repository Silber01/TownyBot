from PIL import Image, ImageEnhance
import json
import random
import discord
from tbLib.playerData import *
from tbLib.townsData import *
from tbLib.tbutils import makeEmbed


async def getMap(ctx, arg, mapType):                            # handles possible errors for regular and for sale maps, then calls if no errors
    if arg == "NONE":
        townID = getPlayerTown(ctx.author.id)
    else:
        townID = findTownID(arg)
    if townID is None:                                          # if player puts in a town name that doesnt exist
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


def makeMap(townID):                                        # makes a map using Pillow by tiling all plots in the town's save data in appropriate places
    townMap = Image.open("images/layout.png")
    with open(f"towns/{townID}.json", "r") as readFile:
        townData = json.load(readFile)
    for y in range(10):
        for x in range(10):
            offset = (64 * (x + 1), 64 * (y + 1))           #tiles are 64x64, so makes a tuple for coordinates based on the plot's positioning
            removeColor = False
            tileID = chr(y + 65) + str(x)
            tileName = getTile(townData, tileID)
            if tileID not in townData["PLOTS"]:             # if the plot is not in the town data, it becomes a greyed out plains tile
                removeColor = True
            tile = Image.open(f"images/{tileName}.png")
            if removeColor:
                tile = tile.convert("L")
            townMap.paste(tile, offset)
    fileName = f"images/maps/{townID}.png"
    townMap.save(fileName)                                  # saves the image and returns the image file name
    return fileName


def makeOwnerMap(townID, resident):                         #same logic as makeMap, but darkens all plots where the user does not own the plot
    ownerMap = Image.open("images/layout.png")
    with open(f"towns/{townID}.json", "r") as readFile:
        townData = json.load(readFile)
    for y in range(10):
        for x in range(10):
            offset = (64 * (x + 1), 64 * (y + 1))           #tiles are 64x64, so makes a tuple for coordinates based on the plot's positioning
            removeColor = False
            darken = False
            tileID = chr(y + 65) + str(x)
            tileName = getTile(townData, tileID)
            if tileID not in townData["PLOTS"]:             # if the plot is not in the town data, it becomes a greyed out plains tile
                removeColor = True
            elif townData["PLOTS"][tileID]["OWNER"] != resident:    # if the plot is in the town but the user does not own the plot, darken it
                darken = True
            tile = Image.open(f"images/{tileName}.png")
            if removeColor:
                tile = tile.convert("L")
            if darken:
                tile = ImageEnhance.Brightness(tile).enhance(0.5)
            ownerMap.paste(tile, offset)
    fileName = f"images/maps/{townID}{resident}.png"
    ownerMap.save(fileName)                                 # saves the image and returns the image file name
    return fileName


def makeForSaleMap(townID):                                 #same logic as makeMap, but darkens all plots that are not for sale
    ownerMap = Image.open("images/layout.png")              # code very similar to makeMap, refer to comments there
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
        return random.choice(tileTypes["PLAIN"])                                # returns a random sprite for plains
    return random.choice(tileTypes[townData["PLOTS"][tileID]["PLOTTYPE"]])      # returns a random sprite for the tile specified
