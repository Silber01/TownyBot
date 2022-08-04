import random

import discord
import os
import asyncio

from tbLib.identifier import identify, getFullName, isNumInLimits
from tbLib.makeEmbed import makeEmbed
from tbLib.playerData import *


# goes through all current dice requests and decreases their time to live by a given amount
# also deletes expired requests
async def deqDiceTTLs(client, seconds):
    for dice in os.listdir("dicereqs"):                         # goes through all dice games
        with open(f"dicereqs/{dice}", "r") as read_file:
            diceData = json.load(read_file)                     # fetches data for the dice game, mainly to check and decrement its ttl
        if diceData["TTL"] <= 0:                                # if ttl is expired, alert the channel the dice request was made in and delete the request
            senderName = getFullName(diceData["SENDER"])
            receiverName = getFullName(diceData["RECEIVER"])
            embed = makeEmbed()
            embed.description = f"**{senderName}**'s dice against **{receiverName}** expired!"
            embed.color = discord.Color.red()
            await client.get_channel(diceData["CHANNEL"]).send(embed=embed)
            os.remove(f"dicereqs/{dice}")                       # removes the dice game
        else:
            diceData["TTL"] -= seconds                          # decrements the ttl
            with open(f"dicereqs/{dice}", "w") as write_file:
                json.dump(diceData, write_file)                 # dumps the modified dice data to the JSON file it came from


# handles the process for making dice requests
async def diceHandler(ctx, receiver, dicesize, dices, winmethod, amount):
    embed = makeEmbed()
    embed.color = discord.Color.red()
    minDiceSize = 2                                             # minimum sides a die can have
    maxDiceSize = 1000000000                                    # maximum sides a die can have
    minDices = 1                                                # minimum amount of dice to roll
    maxDices = 10                                               # maximum amount of dice to roll
    winMethods = ["high", "low", "total", "wins"]               # all possible rulesets players can use
    ttl = 150

    with open("non-code/initdice.json", "r") as read_file:      # fetches init data for a dice game
        diceData = json.load(read_file)
    diceData["SENDER"] = str(ctx.author.id)                     # sets dice sender to the sender's ID
    receiverID = identify(receiver)                             # fetches the receiver's ID
    if receiverID.startswith("ERROR"):                          # if the given receiver's ID is invalid, identify returns "ERROR" followed by an error message
        embed.description = receiverID.replace("ERROR ", "")    # sends the error message and returns
        await ctx.send(embed=embed)
        return
    if str(ctx.author.id) == receiverID:                        # check for if sender is attempting to dice themselves
        embed.description = "You cannot dice yourself!"
        await ctx.send(embed=embed)
        return
    if isInDice(str(ctx.author.id)):                            # check for if sender is already in a game
        embed.description = "You are already in a game!"
        await ctx.send(embed=embed)
        return
    if isInDice(receiverID):                                    # check for if receiver is already in a game
        embed.description = getFullName(receiverID) + " is already in a game!"
        await ctx.send(embed=embed)
        return
    diceSizeCheck = isNumInLimits(dicesize, minDiceSize, maxDiceSize)
    if diceSizeCheck == "NaN":                                  # check for if dice size is not a number
        embed.description = "Dice size is not a number!"
        await ctx.send(embed=embed)
        return
    elif diceSizeCheck == "LOW":                                # check for if dice size is too low
        embed.description = "Dice size is too low. It must have at least " + str(minDiceSize) + " sides."
        await ctx.send(embed=embed)
        return
    elif diceSizeCheck == "HIGH":                               # check for if dice size is too high
        embed.description = "Dice size is too high. It must have at most " + str(maxDiceSize) + " sides."
        await ctx.send(embed=embed)
        return
    dicesCheck = isNumInLimits(dices, minDices, maxDices)
    if dicesCheck == "NaN":                                     # check for if amount of dice rolls is not a number
        embed.description = "Amount of dices is not a number!"
        await ctx.send(embed=embed)
        return
    elif dicesCheck == "LOW":                                   # check for if amount of dice rolls is too low
        embed.description = "Not enough dice. There must be at least " + str(minDices) + " dice."
        await ctx.send(embed=embed)
        return
    elif dicesCheck == "HIGH":                                  # check for if amount of dice rolls is too high
        embed.description = "Too many dice. There must be at most " + str(maxDices) + " dice"
        await ctx.send(embed=embed)
        return
    if winmethod.lower() not in winMethods:                     # check for if specified win method is invalid
        embed.description = """Invalid win method. Please pick from "high", "low", "wins", or "total"."""
        await ctx.send(embed=embed)
        return
    senderBal = getPlayerBalance(ctx.author.id)
    receiverBal = getPlayerBalance(receiverID)
    if amount.lower() == "max":
        amount = min(senderBal, receiverBal)
    else:
        amountCheck = isNumInLimits(amount, 1, min(senderBal, receiverBal))
        if amountCheck == "NaN":                                    # check for if given amount is not a number
            embed.description = "Amount is not a number!"
            await ctx.send(embed=embed)
            return
        elif amountCheck == "LOW":                                  # check for if given amount is too low
            embed.description = "You must bet at least $1"
            await ctx.send(embed=embed)
            return
        elif amountCheck == "HIGH":                                 # check for if given amount is too high
            if int(amount) > senderBal:                             # if sender cannot afford given amount, say sender cannot afford the bet. Else, say receiver cannot afford the bet
                embed.description = "You cannot afford this!"
            else:
                embed.description = "Your opponent cannot afford this!"
            await ctx.send(embed=embed)
            return
    # after all checks, initialize given data into the dicereq dict to make a JSON file
    diceData["RECEIVER"] = receiverID
    diceData["DICESIZE"] = int(dicesize)
    diceData["DICES"] = int(dices)
    diceData["WINMETHOD"] = winmethod.lower()
    diceData["AMOUNT"] = int(amount)
    diceData["CHANNEL"] = ctx.channel.id                        # channel is given just in case the game expires, the "Dice Expired!" message has a place to be sent
    diceData["TTL"] = ttl                                       # ttl is given so that dicereqs can eventually die
    with open(f"dicereqs/{ctx.author.id}.json", "w") as write_file:
        json.dump(diceData, write_file)                         # dump given data into a JSON file
    # setup flavor text and expiration notice, then send
    embed.description = f"""__**DICE GAME STARTED**__\n\n **{getFullName(str(ctx.author.id))}** has challenged **{getFullName(receiverID)}** to a dice game!\n
                        **{dices} {dicesize}**-sided dice will be rolled, and the win condition is **"{winmethod}"**!\n
                        Both players are putting in $**{amount}**, and winner takes all!
                        \n{getFullName(receiverID)}, do `-dice accept` to accept the dice request, or `-dice deny` to deny the dice request.
                        \n{getFullName(str(ctx.author.id))}, do `-dice cancel` to cancel the dice game."""
    embed.set_footer(text="This request expires in " + str(int(ttl / 60)) + " minutes, " + str(ttl % 60) + " seconds.")
    embed.color = discord.Color.green()
    await ctx.send(embed=embed)


# handles for if a user wants to deny a received dice request
async def denyHandler(ctx):
    receiverID = str(ctx.author.id)
    diceToCancel = None                                         # initialized to none just in case there is no dice game sent to user
    for dice in os.listdir("dicereqs"):                         # checks all dice games until it finds one where user is the receiver
        with open(f"dicereqs/{dice}", "r") as read_file:
            if json.load(read_file)["RECEIVER"] == receiverID:
                diceToCancel = dice
                break
    embed = makeEmbed()
    if diceToCancel is None:                                    # check for if user is not in a dice game
        embed.description = "You are not in a dice game!"
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return
    embed.description = f"{getFullName(receiverID)} cancelled the game."
    embed.color = discord.Color.red()
    os.remove(f"dicereqs/{diceToCancel}")                       # removes the dice game
    await ctx.send(embed=embed)


# handles for if user wants to cancel a game they sent
async def cancelHandler(ctx):
    senderID = str(ctx.author.id)
    embed = makeEmbed()
    if senderID + ".json" in os.listdir("dicereqs"):            # checks if there is a dice request named after user
        embed.description = f"{getFullName(senderID)} has cancelled the game."
        embed.color = discord.Color.red()
        os.remove(f"dicereqs/{senderID}.json")                  # removes the dice game
        await ctx.send(embed=embed)
    else:
        embed.description = "You are not in a dice game!"       # lets user know if they are not in a dice game
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)


# handles when a user accepts a dice request
async def acceptHandler(ctx):
    receiverID = str(ctx.author.id)                             # since the receiver accepts the dice request, the author of the accept command is the receiver
    diceGame = None                                             # it is possible there is no dice game the accepter is in, so first checks if a game exists
    for dice in os.listdir("dicereqs"):                         # iterates through all dice games until it finds one where the user is the receiver
        with open(f"dicereqs/{dice}", "r") as read_file:
            if json.load(read_file)["RECEIVER"] == receiverID:
                diceGame = dice
                break
    if diceGame is None:                                        # check for if user is not in a dice game
        embed = makeEmbed()
        embed.description = "You are not in a dice game!"
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return
    with open(f"dicereqs/{diceGame}", "r") as read_file:
        diceData = json.load(read_file)                         # fetches data for the dice game
    senderID = diceData["SENDER"]
    senderName = getFullName(diceData["SENDER"])                # gets full name of sender (username and 4 digit discriminator i.e. Silver01#2371)
    receiverName = getFullName(diceData["RECEIVER"])            # gets full name of receiver
    senderDice = []                                             # initialize array for sender, where the values of the dice they roll are stored
    receiverDice = []                                           # initialize array for receiver
    dices = diceData["DICES"]
    diceSize = diceData["DICESIZE"]
    receiverData = getPlayerData(receiverID)                    # receives data for receiver, to check and edit balance
    senderData = getPlayerData(senderID)                        # receives data for sender
    if receiverData["BALANCE"] < diceData["AMOUNT"]:            # double check for if receiver can still afford the dice game
        embed = makeEmbed()
        embed.description = f"{getFullName(receiverID)} does not have enough money!"
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return
    if senderData["BALANCE"] < diceData["AMOUNT"]:              # double check for if sender can still afford the dice game
        embed = makeEmbed()
        embed.description = f"{getFullName(senderID)} does not have enough money!"
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return
    diceData["TTL"] = 1000                                      # sets ttl to 1000 to avoid it expiring while the game is going
    with open(f"dicereqs/{diceGame}", "w") as write_file:  # dumps dice data to establish new ttl
        json.dump(diceGame, write_file)
    senderData["BALANCE"] -= diceData["AMOUNT"]                 # removes bet money from sender. This and the receiver money will be given back to the winner after the dice
    receiverData["BALANCE"] -= diceData["AMOUNT"]               # removes bet money from receiver
    setPlayerData(receiverID, receiverData)                     # dumps new receiver data to receiver's JSON file to save changes to balance
    setPlayerData(senderID, senderData)                         # dumps sender data
    for i in range(dices):                                      # rolls the dices
        senderRoll = random.randint(0, diceSize)                # gets a random numer from 0 to the size of the dice for the sender
        await asyncio.sleep(0.1)                                # waits for a little bit of time to let the way random seeding works to be more random
        receiverRoll = random.randint(0, diceSize)              # gets dice roll for receiver
        embed = makeEmbed()
        embed.description = f"""**{senderName}** rolled a {senderRoll} on a {diceSize} sided dice.\n
                                **{receiverName}** rolled a {receiverRoll} on a {diceSize} sided dice.\n"""
        await ctx.send(embed=embed)
        senderDice.append(senderRoll)                           # saves sender dice roll
        receiverDice.append(receiverRoll)                       # saves receiver dice roll
        await asyncio.sleep(2)                                  # waits 2 seconds for dramatic effect
    winCondition = diceData["WINMETHOD"]
    winner = None                                               # initialized to None because it is possible there is no winner via a tie
    if winCondition == "high":                                  # gets player summaries and winner for if win condition is "high"
        senderResult = "rolled a high of **" + str(max(senderDice)) + "**."
        receiverResult = "rolled a high of **" + str(max(receiverDice)) + "**."
        if max(senderDice) > max(receiverDice):
            winner = senderID
        elif max(senderDice) < max(receiverDice):
            winner = receiverID
    elif winCondition == "low":                                 # gets player summaries and winner for if win condition is "low"
        senderResult = "rolled a low of **" + str(min(senderDice)) + "**."
        receiverResult = "rolled a low of **" + str(min(receiverDice)) + "**."
        if min(senderDice) < min(receiverDice):
            winner = senderID
        elif min(senderDice) > min(receiverDice):
            winner = receiverID
    elif winCondition == "wins":                                # gets player summaries and winner for if win condition is "wins"
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
    else:                                                                       # gets player summaries and winner for if win condition is "total."
        senderResult = "rolled a total of **" + str(sum(senderDice)) + "**."    # Also acts as the default in case an invalid win method somehow is encountered
        receiverResult = "rolled a total of **" + str(sum(receiverDice)) + "**."
        if sum(senderDice) > sum(receiverDice):
            winner = senderID
        elif sum(senderDice) < sum(receiverDice):
            winner = receiverID
    embed = makeEmbed()
    if winner is None:                                          # handles ties
        embed.description = f"**{senderName}** {senderResult}\n**{receiverName}** {receiverResult}\n\nIt's a tie!"
        embed.color = discord.Color.blue()
        await ctx.send(embed=embed)

        changePlayerBalance(senderID, diceData["AMOUNT"])       # gives back the money to the players
        changePlayerBalance(receiverID, diceData["AMOUNT"])
        os.remove(f"dicereqs/{diceGame}")                       # removes the dice game
        return
    pot = diceData["AMOUNT"] * 2                                # since two players added to the pot, the pot is twice the amount any player gave
    winnerName = getFullName(winner)
    embed.description = f"""**{senderName}** {senderResult}\n**{receiverName}** {receiverResult}\n\n{winnerName} wins! They receive **${pot}**"""
    changePlayerBalance(winner, pot)                            # gives winner the pot money
    embed.color = discord.Color.green()
    await ctx.send(embed=embed)
    os.remove(f"dicereqs/{diceGame}")                           # removes dice game


# checks if a given user is currently in a dice game
def isInDice(diceID):
    if diceID + ".json" in os.listdir("dicereqs"):              # checks if user has sent a dice request by seeing if a dice request named after them exists
        return True
    for dice in os.listdir("dicereqs"):                         # iterates through all dice reqs and sees if the user is the receiver in any of them
        with open(f"dicereqs/{dice}", "r") as read_file:
            if json.load(read_file)["RECEIVER"] == diceID:      # fetches dice req and checks receiver
                return True
    return False                                                # return false if no trace of the given user appears
