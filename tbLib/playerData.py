import json

playerDir = "players"


def getPlayerData(playerID):
    with open(f"{playerDir}/{str(playerID)}.json", "r") as readFile:
        return json.load(readFile)


def setPlayerData(playerID, playerData):
    with open(f"{playerDir}/{str(playerID)}.json", "w") as writeFile:
        json.dump(playerData, writeFile)


def getPlayerBalance(playerID):
    return getPlayerData(playerID)["BALANCE"]


def changePlayerBalance(playerID, amount):
    playerData = getPlayerData(playerID)
    playerData["BALANCE"] += amount
    setPlayerData(playerID, playerData)

