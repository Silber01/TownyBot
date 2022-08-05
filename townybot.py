import json  # allows reading and writing of JSON files
import os
import random

import discord
from discord.ext import commands  # provides the bulk of discord bot abilities
import asyncio

from tbLib.help import helpHandler, commandsHandler
from tbLib.nameGenerator import generateName
from tbLib.stats import statsHandler, balanceHandler, levelsHandler, baltopHandler
from tbLib.jobs import mineHandler, chopHandler, harvestHandler, catchHandler
from tbLib.dicing import diceHandler, deqDiceTTLs, denyHandler, cancelHandler, acceptHandler
from tbLib.pay import payHandler
from tbLib.townycommands import townCommandsHandler, plotCommandsHandler
from tbLib.playerData import *
from tbLib.plots import plotInfo

client = commands.Bot(command_prefix='-', help_command=None)  # sets prefix and deletes default help command

botTitle = "TownyBot"


@client.event
async def on_ready():
    print("I'm ready!")
    while True:
        await asyncio.sleep(5)
        await deqDiceTTLs(client, 5)


@client.before_invoke
async def common(ctx):
    userID = ctx.author.id
    if str(userID) + ".json" not in os.listdir("players"):
        with open("non-code/initplayer.json", "r") as read_file:
            playerData = json.load(read_file)
        playerData["NAME"] = ctx.author.name
        playerData["DISCRIMINATOR"] = ctx.author.discriminator
        playerData["TOWN"] = None
        with open(f"players/{userID}.json", "w") as write_file:
            json.dump(playerData, write_file)
        return
    playerData = getPlayerData(userID)
    if ctx.author.name != playerData["NAME"] or ctx.author.discriminator != playerData["DISCRIMINATOR"]:
        playerData["NAME"] = ctx.author.name
        playerData["DISCRIMINATOR"] = ctx.author.discriminator
        setPlayerData(userID, playerData)


# --------- Help ---------------
@client.command()
async def help(ctx):
    await helpHandler(ctx)


@client.command()
async def commands(ctx):
    await commandsHandler(ctx)


# --------- Stats ---------------
@client.command()
async def stats(ctx, name="NONE"):
    await statsHandler(ctx, name)


@client.command()
async def balance(ctx, name="NONE"):
    await balanceHandler(ctx, name)


@client.command()
async def bal(ctx, name="NONE"):
    await balanceHandler(ctx, name)


@client.command()
async def levels(ctx, name="NONE"):
    await levelsHandler(ctx, name)


@client.command()
async def baltop(ctx, page=1):
    await baltopHandler(ctx, page)


# -------- Jobs ---------------
@client.command()
async def mine(ctx):
    await mineHandler(ctx)


@client.command()
async def chop(ctx):
    await chopHandler(ctx)


@client.command()
async def harvest(ctx):
    await harvestHandler(ctx)

@client.command()
async def farm(ctx):
    await harvestHandler(ctx)


@client.command()
async def catch(ctx):
    await catchHandler(ctx)

@client.command()
async def fish(ctx):
    await catchHandler(ctx)


# -------- Town ---------------
@client.command()
async def town(ctx, *args):
    argsAsList = []
    for arg in args:
        argsAsList.append(arg)
    await townCommandsHandler(ctx, argsAsList, client)


@client.command()
async def t(ctx, *args):
    argsAsList = []
    for arg in args:
        argsAsList.append(arg)
    await townCommandsHandler(ctx, argsAsList, client)

@client.command()
async def plot(ctx, *args):
    argsAsList = []
    for arg in args:
        argsAsList.append(arg)
    await plotCommandsHandler(ctx, argsAsList, client)


# -------- Dicing ---------------
@client.command()
async def dice(ctx, *args):
    if len(args) == 1:
        if args[0].lower() == "deny":
            await denyHandler(ctx)
            return
        elif args[0].lower() == "cancel":
            await cancelHandler(ctx)
            return
        elif args[0].lower() == "accept":
            await acceptHandler(ctx)
            return
    if len(args) < 5:
        await ctx.send(
            "Invalid arguments! Syntax is `-dice <player> <dice size> <dices thrown> <win method (high, low, wins, total)>, <bet>`")
    else:
        await diceHandler(ctx, args[0], args[1], args[2], args[3], args[4])


# --------- Misc -----------
@client.command()
async def pay(ctx, *args):
    if len(args) != 2:
        await ctx.send("Invalid arguments! Syntax is `-pay <player> <amount>")
    await payHandler(ctx, args[0], args[1])

@client.command()
async def egirl(ctx):
    await ctx.send("chloe...")

@client.command()
async def guessNumber(ctx):
    num = random.randint(0, 100)
    guesses = 0
    await ctx.send("I'm thinking of a number from 1 to 100! Guess what the number is!")

    def check(m):
        return m.author == ctx.author
    guess = -1
    while guess != num:
        msg = await client.wait_for("message", check=check)
        try:
            guess = int(msg.content)
        except ValueError:
            await ctx.send("That's not a number!")
        else:
            guesses += 1
            if guess < num:
                await ctx.send(f"Too low, {ctx.author.name}! Try again!")
            elif guess > num:
                await ctx.send(f"Too high, {ctx.author.name}! Try again!")
            else:
                await ctx.send(f"Correct, {ctx.author.name}! The number was {num}, and you got it in {guesses} guesses!")


with open("non-code/key.txt", "r") as readFile:
    token = readFile.read()
client.run(token)
