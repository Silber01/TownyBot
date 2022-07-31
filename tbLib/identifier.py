import os
import json

# Identifies a user from giving a username, username with discriminator, or mention
# Assumes that user data is stored in JSON files with a "NAME" and "DISCRIMINATOR", with the JSON file being the user's ID
# Returns the user ID if user is found, or an error with explanation if user is not found
# Made by Daniel Slade, 2022

userDir = "players"  # Directory for players


def identify(name: str):
    if name.startswith("<@"):                                           # indicates the user pinged the player
        id = name.replace("<@", "").replace(">", "")                    # trims everything except the user ID from the ping
        if id + ".json" in os.listdir(userDir):                         # checks to make sure the pinged person is registered with the bot
            return id
        else:                                                           # throw error for if user exists, but has no account with the bot
            return "ERROR User not registered, have them use this bot!"
    elif "#" in name:                                                   # indicates the user is using the player's discriminator
        userInfo = name.rsplit("#", 1)                                  # splits the name in 2, with userInfo[0] being the name and userInfo[1] being the discriminator
        if len(userInfo[1]) != 4:                                       # checks if discriminator length is 4, if not, then username is invalid
            return "ERROR Invalid username."
        for user in os.listdir("players"):                              # goes through every user until it finds one with same name and discriminator, and returns that user
            with open(f"{userDir}/{user}", "r") as read_file:
                userData = json.load(read_file)
            if userData["NAME"].lower() == userInfo[0].lower() and userData["DISCRIMINATOR"] == userInfo[1]:
                return user.replace(".json", "")
        return "ERROR User does not exist."                             # throws error if user was not found
    else:                                                               # tests to see if user simply put in player's username
        userID = "null"                                                 # initialized to "null" in case user does not exist
        userList = []                                                   # initializes list in case there are multiple instances of a name
        for user in os.listdir("players"):                              # goes through all users and appends player ID's whose names are the name specified
            with open(f"{userDir}/{user}", "r") as read_file:
                userData = json.load(read_file)
            if userData["NAME"].lower() == name.lower():
                userID = user.replace(".json", "")
                username = userData["NAME"]
                discrim = userData["DISCRIMINATOR"]
                userList.append(f"{username}#{discrim}")
        if len(userList) == 1:                                          # if exactly one instance of a player name exists, return that player's ID
            return userID
        elif len(userList) == 0:                                        # if no instances of a player name exists, throw error saying user does not exist
            return "ERROR User does not exist."
        else:                                                           # else, there are multiple instances. Throw error listing all player full names
            errorMsg = "ERROR There are multiple users with this name:\n"
            for i in range(len(userList)):
                errorMsg += f"\n{i + 1}: {userList[i]}"
            errorMsg += "\n\nPlease use their full username with the 4-digit code, or mention them instead of putting their name."
            return errorMsg


# fetches name and discriminator for a player given their ID
def getFullName(id):
    with open(f"players/{id}.json", "r") as read_file:
        playerData = json.load(read_file)
    return playerData["NAME"] + "#" + playerData["DISCRIMINATOR"]


# given a number, low, and high, determines if number is valid, not a number, too low, or too high
def isNumInLimits(number, low, high):
    try:
        value = int(number)
    except ValueError:
        return "NaN"
    if value < low:
        return "LOW"
    if value > high:
        return "HIGH"
    return "VALID"
