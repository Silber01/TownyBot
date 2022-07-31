import random

import discord
import os
import json
import asyncio

from tbLib.identifier import identify, getFullName, isNumInLimits
from tbLib.makeEmbed import makeEmbed
from tbLib.playerData import *


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
    senderBal = getPlayerBalance(ctx.author.id)
    receiverBal = getPlayerBalance(receiverID)
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


async def denyHandler(ctx):
    receiverID = str(ctx.author.id)
    diceToCancel = None
    for dice in os.listdir("dicereqs"):
        with open(f"dicereqs/{dice}", "r") as read_file:
            if json.load(read_file)["RECEIVER"] == receiverID:
                diceToCancel = dice
                break
    embed = makeEmbed()
    if diceToCancel is None:
        embed.description = "You are not in a dice game!"
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return
    embed.description = f"{getFullName(receiverID)} cancelled the game."
    embed.color = discord.Color.red()
    os.remove(f"dicereqs/{diceToCancel}")
    await ctx.send(embed=embed)


async def cancelHandler(ctx):
    senderID = str(ctx.author.id)
    embed = makeEmbed()
    if senderID + ".json" in os.listdir("dicereqs"):
        embed.description = f"{getFullName(senderID)} has cancelled the game."
        embed.color = discord.Color.red()
        os.remove(f"dicereqs/{senderID}.json")
        await ctx.send(embed=embed)
    else:
        embed.description = "You are not in a dice game!"
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)


async def acceptHandler(ctx):
    receiverID = str(ctx.author.id)
    diceGame = None
    for dice in os.listdir("dicereqs"):
        with open(f"dicereqs/{dice}", "r") as read_file:
            if json.load(read_file)["RECEIVER"] == receiverID:
                diceGame = dice
                break
    if diceGame is None:
        embed = makeEmbed()
        embed.description = "You are not in a dice game!"
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return
    with open(f"dicereqs/{diceGame}", "r") as read_file:
        diceData = json.load(read_file)
    senderID = diceData["SENDER"]
    senderName = getFullName(diceData["SENDER"])
    receiverName = getFullName(diceData["RECEIVER"])
    senderDice = []
    receiverDice = []
    dices = diceData["DICES"]
    diceSize = diceData["DICESIZE"]
    receiverData = getPlayerData(receiverID)
    senderData = getPlayerData(senderID)
    if receiverData["BALANCE"] < diceData["AMOUNT"]:
        embed = makeEmbed()
        embed.description = f"{getFullName(receiverID)} does not have enough money!"
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return
    if senderData["BALANCE"] < diceData["AMOUNT"]:
        embed = makeEmbed()
        embed.description = f"{getFullName(senderID)} does not have enough money!"
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return
    senderData["BALANCE"] -= diceData["AMOUNT"]
    receiverData["BALANCE"] -= diceData["AMOUNT"]
    setPlayerData(receiverID, receiverData)
    setPlayerData(senderID, senderData)
    for i in range(dices):
        senderRoll = random.randint(0, diceSize)
        await asyncio.sleep(0.1)
        receiverRoll = random.randint(0, diceSize)
        embed = makeEmbed()
        embed.description = f"""**{senderName}** rolled a {senderRoll} on a {diceSize} sided dice.\n
                                **{receiverName}** rolled a {receiverRoll} on a {diceSize} sided dice.\n"""
        await ctx.send(embed=embed)
        senderDice.append(senderRoll)
        receiverDice.append(receiverRoll)
        await asyncio.sleep(2)
    winCondition = diceData["WINMETHOD"]
    winner = None
    if winCondition == "high":
        senderResult = "rolled a high of **" + str(max(senderDice)) + "**."
        receiverResult = "rolled a high of **" + str(max(receiverDice)) + "**."
        if max(senderDice) > max(receiverDice):
            winner = senderID
        elif max(senderDice) < max(receiverDice):
            winner = receiverID
    elif winCondition == "low":
        senderResult = "rolled a low of **" + str(min(senderDice)) + "**."
        receiverResult = "rolled a low of **" + str(min(receiverDice)) + "**."
        if min(senderDice) < min(receiverDice):
            winner = senderID
        elif min(senderDice) > min(receiverDice):
            winner = receiverID
    elif winCondition == "wins":
        senderWins = 0
        receiverWins = 0
        for i in range(len(senderDice)):
            if senderDice[i] > receiverDice[i]:
                senderWins += 1
            elif senderDice[i] < receiverDice[i]:
                receiverWins += 1
        senderResult = "won **" + str(senderWins) + "** games"
        receiverResult = "won **" + str(receiverWins) + "** games"
        if senderWins > receiverWins:
            winner = senderID
        elif senderWins < receiverWins:
            winner = receiverID
    else:
        senderResult = "rolled a total of **" + str(sum(senderDice)) + "**."
        receiverResult = "rolled a total of **" + str(sum(receiverDice)) + "**."
        if sum(senderDice) > sum(receiverDice):
            winner = senderID
        elif sum(senderDice) < sum(receiverDice):
            winner = receiverID
    embed = makeEmbed()
    if winner is None:
        embed.description = f"**{senderName}** {senderResult}\n**{receiverName}** {receiverResult}\n\nIt's a tie!"
        embed.color = discord.Color.blue()
        await ctx.send(embed=embed)

        changePlayerBalance(senderID, diceData["AMOUNT"])
        changePlayerBalance(receiverID, diceData["AMOUNT"])
        os.remove(f"dicereqs/{diceGame}")
        return
    pot = diceData["AMOUNT"] * 2
    winnerName = getFullName(winner)
    embed.description = f"""**{senderName}** {senderResult}\n**{receiverName}** {receiverResult}\n\n{winnerName} wins! They receive **${pot}**"""
    changePlayerBalance(winner, pot)
    embed.color = discord.Color.green()
    await ctx.send(embed=embed)
    os.remove(f"dicereqs/{diceGame}")

def isInDice(diceID):
    if diceID + ".json" in os.listdir("dicereqs"):
        return True
    for dice in os.listdir("dicereqs"):
        with open(f"dicereqs/{dice}", "r") as read_file:
            if json.load(read_file)["RECEIVER"] == diceID:
                return True
    return False
