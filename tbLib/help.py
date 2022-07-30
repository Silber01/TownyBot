import discord
from discord.ext import commands

botTitle = "TownyBot"


async def helpHandler(ctx):
    with open("non-code/help.txt", "r") as read_file:
        helpText = read_file.read()
    embed = discord.Embed(title=botTitle)
    embed.description = helpText
    embed.colour = discord.Colour.blue()
    await ctx.send(embed=embed)


async def commandsHandler(ctx):
    with open("non-code/commands.txt", "r") as read_file:
        commandsText = read_file.read()
    embed = discord.Embed(title=botTitle)
    embed.description = commandsText
    embed.colour = discord.Colour.purple()
    await ctx.send(embed=embed)