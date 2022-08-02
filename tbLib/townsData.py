import os
import json

from tbLib.playerData import *


def getTownName(townID):
    if townID + ".json" not in os.listdir("towns"):
        return "none"
    return getTownData(townID)["NAME"]


def findTownID(townName):
    for town in os.listdir("towns"):
        town = town.replace(".json", "")
        if getTownData(town)["NAME"].lower() == townName.lower():
            return town
    return "NONE"


def isMayor(playerID):
    if getPlayerTown(playerID) == "NONE":
        return False
    townData = getTownData(getPlayerTown(playerID))
    if townData["MAYOR"] == playerID:
        return True
    return False


def getTownData(townID):
    with open(f"towns/{townID}.json", "r") as read_file:
        return json.load(read_file)


def setTownData(townID, townData):
    with open(f"towns/{townID}.json", "w") as write_file:
        json.dump(townData, write_file)
