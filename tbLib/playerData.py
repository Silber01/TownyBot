import json

playerDir = "players"


# fetches player data given their ID
def getPlayerData(playerID):
    with open(f"{playerDir}/{str(playerID)}.json", "r") as readFile:
        return json.load(readFile)


# dumps given playerData to the JSON file for the given playerID
def setPlayerData(playerID, playerData):
    with open(f"{playerDir}/{str(playerID)}.json", "w") as writeFile:
        json.dump(playerData, writeFile)


# returns balance of given player
def getPlayerBalance(playerID):
    return getPlayerData(playerID)["BALANCE"]


# returns town ID of given player
def getPlayerTown(playerID):
    return getPlayerData(playerID)["TOWN"]


# changes the balance of a given player by a given amount
def changePlayerBalance(playerID, amount):
    playerData = getPlayerData(playerID)
    playerData["BALANCE"] += amount
    setPlayerData(playerID, playerData)
