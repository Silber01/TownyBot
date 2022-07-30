import discord
import json
from tbLib.identifier import identify
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




