import os

import discord
import json
from tbLib.identifier import identify, getFullName
from tbLib.makeEmbed import makeEmbed
from tbLib.jobs import calculateNextLevel


async def identifyAndHandleError(ctx, name):
    embed = makeEmbed()
    if name == "NONE":
        userID = ctx.author.id
    else:
        userID = identify(name)
        if userID.startswith("ERROR"):
            embed.description = userID.replace("ERROR ", "")
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return "ERROR"
    return userID


async def statsHandler(ctx, name):
    embed = makeEmbed()
    userID = await identifyAndHandleError(ctx, name)
    if userID == "ERROR":
        return
    with open(f"players/{userID}.json", "r") as read_file:
        userData = json.load(read_file)
    with open("non-code/stats.txt") as read_file:
        statsMsg = read_file.read()
    statsMsg = statsMsg.replace("USERNAME", userData["NAME"])
    statsMsg = statsMsg.replace("BALANCE", str(userData["BALANCE"]))
    statsMsg = statsMsg.replace("TOWN", userData["TOWN"])
    statsMsg = statsMsg.replace("MINELVL", str(userData["MINELVL"]))
    statsMsg = statsMsg.replace("WOODLVL", str(userData["WOODLVL"]))
    statsMsg = statsMsg.replace("FARMINGLVL", str(userData["FARMLVL"]))
    statsMsg = statsMsg.replace("FISHINGLVL", str(userData["FISHLVL"]))
    embed.description = statsMsg
    await ctx.send(embed=embed)


async def balanceHandler(ctx, name):
    embed = makeEmbed()
    userID = await identifyAndHandleError(ctx, name)
    if userID == "ERROR":
        return
    with open(f"players/{userID}.json", "r") as read_file:
        userData = json.load(read_file)
    username = userData["NAME"]
    balance = userData["BALANCE"]
    embed.description = f"**{username}'s balance**: ${balance}"
    await ctx.send(embed=embed)

async def levelsHandler(ctx, name):
    embed = makeEmbed()
    userID = await identifyAndHandleError(ctx, name)
    if userID == "ERROR":
        return
    with open(f"players/{userID}.json", "r") as read_file:
        userData = json.load(read_file)
    with open("non-code/levels.txt", "r") as read_file:
        levelsMsg = read_file.read()
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
    await ctx.send(embed=embed)


async def baltopHandler(ctx, page):
    users = {}
    for user in os.listdir("players"):
        with open(f"players/{user}", "r") as read_file:
            userData = json.load(read_file)
        userName = getFullName(user.replace(".json", ""))
        userBal = userData["BALANCE"]
        users[userName] = userBal
    sortedUsers = sorted(users.items(), key=lambda x: x[1], reverse=True)
    embed = makeEmbed()
    embed.description = "**__Baltop:__**\n"
    place = 0
    leaderboardSize = 10
    startPlace = (int(page) - 1) * leaderboardSize
    leaderboard = []
    authorPos = 0
    for user in sortedUsers:
        if user[0] == getFullName(str(ctx.author.id)):
            authorPos = place + 1
        if startPlace <= place < startPlace + leaderboardSize:
            userStats = [f"{place + 1}. **{user[0]}**", user[1]]
            leaderboard.append(userStats)
        place += 1
    for user in leaderboard:
        embed.description += "\n" + user[0] + ": $" + str(user[1])

    embed.set_footer(text="You are in position #" + str(authorPos))
    await ctx.send(embed=embed)


