import json
import os
import discord

from tbLib.identifier import identify, getFullName, isNumInLimits
from tbLib.makeEmbed import makeEmbed
from tbLib.playerData import *

# handles pay command
async def payHandler(ctx, person, amount):
    embed = makeEmbed()
    embed.color = discord.Color.red()
    senderID = str(ctx.author.id)                                   # fetches sender ID
    receiverID = identify(person)                                   # fetches receiverID
    if receiverID.startswith("ERROR"):                              # if there was an error fetching receiverID, show the error
        embed.description = receiverID.replace("ERROR ", "")
        await ctx.send(embed=embed)
        return
    senderData = getPlayerData(senderID)                            # fetch sender data
    canSend = isNumInLimits(amount, 1, senderData["BALANCE"])       # sends amount to isNumInLimits to make sure it is a number, positive, and the sender can afford it
    if canSend == "NaN":                                            # checks if amount specified is not a number
        embed.description = "Please enter a number for the amount you want to pay."
        await ctx.send(embed=embed)
        return
    elif canSend == "LOW":                                          # checks if amount specified is too low
        embed.description = "Specified amount must be positive."
        await ctx.send(embed=embed)
        return
    elif canSend == "HIGH":                                         # checks if amount is too high
        embed.description = "You cannot afford to do that!"
        await ctx.send(embed=embed)
        return
    embed.description = f"{getFullName(senderID)} has successfully paid {getFullName(receiverID)} **${amount}**."
    await ctx.send(embed=embed)
    receiverData = getPlayerData(receiverID)                        # fetches receiver data
    senderData["BALANCE"] -= int(amount)                            # deducts money from sender
    receiverData["BALANCE"] += int(amount)                          # gives money to receiver
    setPlayerData(senderID, senderData)                             # sets sender data
    setPlayerData(receiverID, receiverData)                         # sets receiver data
