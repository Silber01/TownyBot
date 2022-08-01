from PIL import Image, ImageEnhance
import json
import random


def makeMap(townID):
    townMap = Image.open("images/layout.png")
    with open(f"towns/{townID}.json", "r") as readFile:
        townData = json.load(readFile)
    for y in range(10):
        for x in range(10):
            offset = (32 * (x + 1), 32 * (y + 1))
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
            offset = (32 * (x + 1), 32 * (y + 1))
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
            offset = (32 * (x + 1), 32 * (y + 1))
            removeColor = False
            darken = False
            tileID = chr(y + 65) + str(x)
            tileName = getTile(townData, tileID)
            if tileID not in townData["PLOTS"]:
                removeColor = True
            elif tileID not in townData["FORSALE"]:
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
    if tileID not in townData["PLOTS"]:  # Plot not owned by town, pick a random plains tile
        randNum = random.randint(0, 10)
        if randNum == 1:
            return "plain1"
        elif randNum == 2:
            return "plain2"
        else:
            return "plain"
    else:
        return townData["PLOTS"][tileID]["PLOTTYPE"].lower()
