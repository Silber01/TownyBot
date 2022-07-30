import discord
import os
import json

from tbLib.identifier import identify, getFullName
from tbLib.makeEmbed import makeEmbed


async def deqDiceTTLs(client, seconds):
    for dice in os.listdir("dicereqs"):
        with open(f"dicereqs/{dice}", "r") as read_file:
            diceData = json.load(read_file)
        if diceData["TTL"] <= 0:
            senderName = getFullName(diceData["SENDER"])
            receiverName = getFullName(diceData["RECEIVER"])
            embed = makeEmbed()
            embed.description = f"**{senderName}**'s dice against **{receiverName}** expired!"
            embed.color = discord.Color.red()
            await client.get_channel(diceData["CHANNEL"]).send(embed=embed)
            os.remove(f"dicereqs/{dice}")
        else:
            diceData["TTL"] -= seconds
            with open(f"dicereqs/{dice}", "w") as write_file:
                json.dump(diceData, write_file)


async def diceHandler(ctx, receiver, dicesize, dices, winmethod, amount):
    embed = makeEmbed()
    embed.color = discord.Color.red()
    minDiceSize = 2
    maxDiceSize = 1000
    minDices = 1
    maxDices = 10
    winMethods = ["high", "low", "total", "wins"]
    ttl = 150

    with open("non-code/initdice.json", "r") as read_file:
        diceData = json.load(read_file)
    diceData["SENDER"] = str(ctx.author.id)
    receiverID = identify(receiver)
    if receiverID.startswith("ERROR"):
        embed.description = receiverID.replace("ERROR ", "")
        await ctx.send(embed=embed)
        return
    if str(ctx.author.id) == receiverID:
        embed.description = "You cannot dice yourself!"
        await ctx.send(embed=embed)
        return
    if isInDice(str(ctx.author.id)):
        embed.description = "You are already in a game!"
        await ctx.send(embed=embed)
        return
    if isInDice(receiverID):
        embed.description = getFullName(receiverID) + " is already in a game!"
        await ctx.send(embed=embed)
        return
    diceSizeCheck = isNumInLimits(dicesize, minDiceSize, maxDiceSize)
    if diceSizeCheck == "NaN":
        embed.description = "Dice size is not a number!"
        await ctx.send(embed=embed)
        return
    elif diceSizeCheck == "LOW":
        embed.description = "Dice size is too low. It must have at least " + str(minDiceSize) + " sides."
        await ctx.send(embed=embed)
        return
    elif diceSizeCheck == "HIGH":
        embed.description = "Dice size is too high. It must have at most " + str(maxDiceSize) + " sides."
        await ctx.send(embed=embed)
        return
    dicesCheck = isNumInLimits(dices, minDices, maxDices)
    if dicesCheck == "NaN":
        embed.description = "Amount of dices is not a number!"
        await ctx.send(embed=embed)
        return
    elif dicesCheck == "LOW":
        embed.description = "Not enough dice. There must be at least " + str(minDices) + " dice."
        await ctx.send(embed=embed)
        return
    elif dicesCheck == "HIGH":
        embed.description = "Too many dice. There must be at most " + str(maxDices) + " dice"
        await ctx.send(embed=embed)
        return
    if winmethod.lower() not in winMethods:
        embed.description = """Invalid win method. Please pick from "high", "low", "wins", or "total"."""
        await ctx.send(embed=embed)
        return
    with open(f"players/{ctx.author.id}.json", "r") as read_file:
        senderBal = int(json.load(read_file)["BALANCE"])
    with open(f"players/{receiverID}.json", "r") as read_file:
        receiverBal = int(json.load(read_file)["BALANCE"])
    amountCheck = isNumInLimits(amount, 1, min(senderBal, receiverBal))
    if amountCheck == "NaN":
        embed.description = "Amount is not a number!"
        await ctx.send(embed=embed)
        return
    elif amountCheck == "LOW":
        embed.description = "You must bet at least $1"
        await ctx.send(embed=embed)
        return
    elif amountCheck == "HIGH":
        if int(amount) > senderBal:
            embed.description = "You cannot afford this!"
        else:
            embed.description = "Your opponent cannot afford this!"
        await ctx.send(embed=embed)
        return

    diceData["RECEIVER"] = receiverID
    diceData["DICESIZE"] = int(dicesize)
    diceData["DICES"] = int(dices)
    diceData["WINMETHOD"] = winmethod.lower()
    diceData["AMOUNT"] = int(amount)
    diceData["CHANNEL"] = ctx.channel.id
    diceData["TTL"] = ttl
    with open(f"dicereqs/{ctx.author.id}.json", "w") as write_file:
        json.dump(diceData, write_file)

    embed.description = f"""__**DICE GAME STARTED**__\n\n **{getFullName(str(ctx.author.id))}** has challenged **{getFullName(receiverID)}** to a dice game!\n
                        **{dices} {dicesize}**-sided dice will be rolled, and the win condition is **"{winmethod}"**!\n
                        Both players are putting in $**{amount}**, and winner takes all!"""
    embed.set_footer(text="This request expires in " + str(int(ttl / 60)) + " minutes, " + str(ttl % 60) + " seconds.")
    embed.color = discord.Color.green()
    await ctx.send(embed=embed)


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


def isInDice(id):
    if id + ".json" in os.listdir("dicereqs"):
        return True
    for dice in os.listdir("dicereqs"):
        with open(f"dicereqs/{dice}", "r") as read_file:
            if json.load(read_file)["RECEIVER"] == id:
                return True
    return False
