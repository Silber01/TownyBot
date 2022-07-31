import json  # allows reading and writing of JSON files
import os
from os.path import exists
import discord  # provides some additional discord features, such as embedded messages
from discord.ext import commands  # provides the bulk of discord bot abilities
import asyncio

from tbLib.help import helpHandler, commandsHandler
from tbLib.nameGenerator import generateName
from tbLib.stats import statsHandler, balanceHandler, levelsHandler
from tbLib.jobs import mineHandler, chopHandler, harvestHandler, catchHandler
from tbLib.dicing import diceHandler, deqDiceTTLs, denyHandler, cancelHandler, acceptHandler

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
        playerData["TOWN"] = generateName()
        with open(f"players/{userID}.json", "w") as write_file:
            json.dump(playerData, write_file)


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
async def catch(ctx):
    await catchHandler(ctx)


# -------- Jobs ---------------


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


with open("non-code/key.txt", "r") as readFile:
    token = readFile.read()
client.run(token)
