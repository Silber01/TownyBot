import os

import discord
import json
from tbLib.identifier import identify, getFullName
from tbLib.makeEmbed import makeEmbed
from tbLib.jobs import calculateNextLevel
from tbLib.playerData import *
from tbLib.townsData import getTownName


# returns stats of specified user
async def statsHandler(ctx, name):
    embed = makeEmbed()
    userID = await identifyAndHandleError(ctx, name)                            # identifies player, or gets error message if specified player not valid
    if userID == "ERROR":                                                       # if error occurs, do nothing here
        return
    userData = getPlayerData(userID)                                            # fetches player ID
    with open("non-code/stats.txt") as read_file:                               # fetches stats.txt
        statsMsg = read_file.read()
    # replace various keywords with wanted values
    statsMsg = statsMsg.format(username=userData["NAME"], balance=userData["BALANCE"], town=getTownName(userData["TOWN"]),
                               minelvl=userData["MINELVL"], woodlvl=userData["WOODLVL"],
                               farminglvl=userData["FARMLVL"], fishinglvl=userData["FISHLVL"],
                               mines=userData["MINES"], forests=userData["FORESTS"],
                               farms=userData["FARMS"], ponds=userData["PONDS"])
    embed.description = statsMsg
    embed.color = discord.Color.purple()
    await ctx.send(embed=embed)


# returns balance of specified user
async def balanceHandler(ctx, name):
    embed = makeEmbed()
    userID = await identifyAndHandleError(ctx, name)                            # identifies player, or gets error message if specified player not valid
    if userID == "ERROR":                                                       # if error occurs, do nothing here
        return
    userData = getPlayerData(userID)
    username = userData["NAME"]
    balance = userData["BALANCE"]
    embed.description = f"**{username}'s balance**: ${balance}"
    embed.color = discord.Color.purple()
    await ctx.send(embed=embed)


async def levelsHandler(ctx, name):
    embed = makeEmbed()
    userID = await identifyAndHandleError(ctx, name)                            # identifies player, or gets error message if specified player not valid
    if userID == "ERROR":                                                       # if error occurs, do nothing here
        return
    userData = getPlayerData(userID)
    with open("non-code/levels.txt", "r") as read_file:                         # fetches levels.txt
        levelsMsg = read_file.read()
    # replace various keywords with wanted values
    levelsMsg = levelsMsg.replace("USERNAME", str(userData["NAME"]))
    levelsMsg = levelsMsg.replace("MINELVL", str(userData["MINELVL"]))
    levelsMsg = levelsMsg.replace("MINEXP", str(userData["MINEXP"]))
    levelsMsg = levelsMsg.replace("WOODLVL", str(userData["WOODLVL"]))
    levelsMsg = levelsMsg.replace("WOODXP", str(userData["WOODXP"]))
    levelsMsg = levelsMsg.replace("FARMLVL", str(userData["FARMLVL"]))
    levelsMsg = levelsMsg.replace("FARMXP", str(userData["FARMXP"]))
    levelsMsg = levelsMsg.replace("FISHLVL", str(userData["FISHLVL"]))
    levelsMsg = levelsMsg.replace("FISHXP", str(userData["FISHXP"]))
    levelsMsg = levelsMsg.replace("MINEREQXP", str(calculateNextLevel(userData["MINELVL"])))
    levelsMsg = levelsMsg.replace("WOODREQXP", str(calculateNextLevel(userData["WOODLVL"])))
    levelsMsg = levelsMsg.replace("FARMREQXP", str(calculateNextLevel(userData["FARMLVL"])))
    levelsMsg = levelsMsg.replace("FISHREQXP", str(calculateNextLevel(userData["FISHLVL"])))
    embed.description = levelsMsg
    embed.color = discord.Color.purple()
    await ctx.send(embed=embed)


# handles baltop
async def baltopHandler(ctx, page):
    users = {}                                                              # initializes dictionary, which will be used to make key-value pairs of full names and balances
    for user in os.listdir("players"):                                      # iterates through all users and adds full name and balance to users
        user = user.replace(".json", "")
        userData = getPlayerData(user)
        userName = getFullName(user)
        userBal = userData["BALANCE"]
        users[userName] = userBal
    sortedUsers = sorted(users.items(), key=lambda x: x[1], reverse=True)   # sorts users by values and stores result in sortedUsers
    embed = makeEmbed()
    embed.description = "**__Baltop:__**\n"
    place = 0                                                               # iterator for placement of user
    leaderboardSize = 10                                                    # determines how many people fit on one page
    startPlace = (int(page) - 1) * leaderboardSize                          # determines where to start by given page value
    leaderboard = []                                                        # initializes empty list for users to be put in
    authorPos = 0
    for user in sortedUsers:                                                # iterates through all users
        if user[0] == getFullName(str(ctx.author.id)):                      # checks if given user is the player that called the command
            authorPos = place + 1
        if startPlace <= place < startPlace + leaderboardSize:              # checks if place is within bounds of the page requested
            userStats = [f"{place + 1}. **{user[0]}**", user[1]]            # adds full name and balance to leaderboard
            leaderboard.append(userStats)
        place += 1
    for user in leaderboard:                                                # adds users to the description
        embed.description += "\n" + user[0] + ": $" + str(user[1])

    embed.set_footer(text="You are in position #" + str(authorPos))         # shows player's position
    embed.color = discord.Color.purple()
    await ctx.send(embed=embed)


# checks if a given user is valid, and, if not, throws error
async def identifyAndHandleError(ctx, name):
    embed = makeEmbed()
    if name == "NONE":                                                      # name not specified, so assume the name is the message author
        userID = ctx.author.id
    else:
        userID = identify(name)                                             # identify user ID
        if userID.startswith("ERROR"):                                      # if identify throws error, print it and return "ERROR"
            embed.description = userID.replace("ERROR ", "")
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return "ERROR"
    return userID
