import os
import json

# Identifies a user from giving a username, username with discriminator, or mention
# Assumes that user data is stored in JSON files with a "NAME" and "DISCRIMINATOR", with the JSON file being the user's ID
# Returns the user ID if user is found, or an error with explanation if user is not found
# Made by Daniel Slade, 2022

userDir = "players"  # Directory for


def identify(name: str):
    if name.startswith("<@"):
        id = name.replace("<@", "").replace(">", "")
        if id + ".json" in os.listdir(userDir):
            return id
        else:
            return "ERROR User not registered, have them use this bot!"
    elif "#" in name:
        userInfo = name.rsplit("#", 1)
        if len(userInfo) != 2:
            return "ERROR Invalid username."
        if len(userInfo[1]) != 4:
            return "ERROR Invalid username."
        for user in os.listdir("players"):
            with open(f"{userDir}/{user}", "r") as read_file:
                userData = json.load(read_file)
            if userData["NAME"].lower() == userInfo[0].lower() and userData["DISCRIMINATOR"] == userInfo[1]:
                return user.replace(".json", "")
        return "ERROR User does not exist."
    else:
        userID = "null"
        userList = []
        for user in os.listdir("players"):
            with open(f"{userDir}/{user}", "r") as read_file:
                userData = json.load(read_file)
            if userData["NAME"].lower() == name.lower():
                userID = user.replace(".json", "")
                username = userData["NAME"]
                discrim = userData["DISCRIMINATOR"]
                userList.append(f"{username}#{discrim}")
        if len(userList) == 1:
            return userID
        elif len(userList) == 0:
            return "ERROR User does not exist."
        else:
            errorMsg = "ERROR There are multiple users with this name:\n"
            for i in range(len(userList)):
                errorMsg += f"\n{i + 1}: {userList[i]}"
            errorMsg += "\n\nPlease use their full username with the 4-digit code, or mention them instead of putting their name."
            return errorMsg


def getFullName(id):
    with open(f"players/{id}.json", "r") as read_file:
        playerData = json.load(read_file)
    return playerData["NAME"] + "#" + playerData["DISCRIMINATOR"]
