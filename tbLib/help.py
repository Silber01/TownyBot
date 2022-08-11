import discord

from tbLib.tbutils import makeEmbed


# prints help page specified
async def helpHandler(ctx, page="NONE"):
    page = page.upper()
    helpPage = "help.txt"
    if page == "COMMANDS":
        helpPage = "commands.txt"
    if page == "TOWNS":
        helpPage = "townyhelp.txt"
    with open(f"non-code/{helpPage}", "r") as read_file:
        helpText = read_file.read()
    embed = makeEmbed()
    embed.description = helpText
    embed.colour = discord.Colour.blue()
    await ctx.send(embed=embed)


# prints commands.txt
async def commandsHandler(ctx):
    with open("non-code/commands.txt", "r") as read_file:
        commandsText = read_file.read()
    embed = makeEmbed()
    embed.description = commandsText
    embed.colour = discord.Colour.purple()
    await ctx.send(embed=embed)
