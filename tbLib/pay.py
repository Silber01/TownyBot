import json
import os
import discord

from tbLib.identifier import identify, getFullName, isNumInLimits
from tbLib.makeEmbed import makeEmbed
from tbLib.playerData import *

async def payHandler(ctx, person, amount):
    embed = makeEmbed()
    embed.color = discord.Color.red()
    senderID = str(ctx.author.id)
    receiverID = identify(person)
    if receiverID.startswith("ERROR"):
        embed.description = receiverID.replace("ERROR ", "")
        await ctx.send(embed=embed)
        return
    senderData = getPlayerData(senderID)
    canSend = isNumInLimits(amount, 1, senderData["BALANCE"])
    if canSend == "NaN":
        embed.description = "Please enter a number for the amount you want to pay."
        await ctx.send(embed=embed)
        return
    elif canSend == "LOW":
        embed.description = "Specified amount must be positive."
        await ctx.send(embed=embed)
        return
    elif canSend == "HIGH":
        embed.description = "You cannot afford to do that!"
        await ctx.send(embed=embed)
        return
    embed.description = f"{getFullName(senderID)} has successfully paid {getFullName(receiverID)} **${amount}**."
    await ctx.send(embed=embed)
    receiverData = getPlayerData(receiverID)
    senderData["BALANCE"] -= int(amount)
    receiverData["BALANCE"] += int(amount)
    setPlayerData(senderID, senderData)
    setPlayerData(receiverID, receiverData)



