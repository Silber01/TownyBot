import discord
import json
from tbLib.identifier import identify
from tbLib.makeEmbed import makeEmbed


async def statsHandler(ctx, name):
    embed = makeEmbed()
    if name == "NONE":
        userID = ctx.author.id
    else:
        userID = identify(name)
        if userID.startswith("ERROR"):
            embed.description = userID.replace("ERROR ", "")
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
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
    statsMsg = statsMsg.replace("FISHINGLVL",  str(userData["FISHLVL"]))
    embed.description = statsMsg
    await ctx.send(embed=embed)





