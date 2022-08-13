import os
import json

from tbLib.playerData import *


def getTownName(townID):                                            # finds the name of a town given its ID
    if townID is None:
        return None
    if townID + ".json" not in os.listdir("towns"):
        return None
    return getTownData(townID)["NAME"]


def findTownID(townName):                                           # finds the ID of a town by its name
    for town in os.listdir("towns"):
        town = town.replace(".json", "")
        if getTownData(town)["NAME"].lower() == townName.lower():
            return town
    return None


def isMayor(playerID):                                              # checks if the player is a mayor of a town
    if getPlayerTown(playerID) is None:                             # trivial case for if player is not in a town at all
        return False
    townData = getTownData(getPlayerTown(playerID))
    if townData["MAYOR"] == playerID:
        return True
    return False


def getTownData(townID):                                            # retrieves town data
    with open(f"towns/{townID}.json", "r") as read_file:
        return json.load(read_file)


def setTownData(townID, townData):                                  # sets town data
    with open(f"towns/{townID}.json", "w") as write_file:
        json.dump(townData, write_file)


def getHouseForSale(townID):                                        # searches for a house that is for sale, and returns
    townData = getTownData(townID)
    for plot in townData["PLOTS"]:
        if townData["PLOTS"][plot]["PLOTTYPE"] == "HOUSEFORSALE":
            return plot
    return None