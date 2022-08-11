import json
import os
import discord

from tbLib.townsData import *
from tbLib.tbutils import makeEmbed
from tbLib.playerData import *
from tbLib.identifier import *

invTTL = 150


def getInviteData(invID):
    with open(f"towninvites/{invID}.json", "r") as read_file:
        return json.load(read_file)


def setInviteData(invID, invData):
    with open(f"towninvites/{invID}.json", "w") as write_file:
        json.dump(invData, write_file)


async def deqTownTTLs(client, amount):
    for inv in os.listdir("towninvites"):
        inv = inv.replace(".json", "")
        invData = getInviteData(inv)
        invData["TTL"] -= amount
        if invData["TTL"] <= 0:
            embed = makeEmbed()
            senderName = getFullName(invData["SENDER"])
            receiverName = getFullName(inv)
            townName = getTownName(invData["TOWN"])
            embed.description = f"**{senderName}**'s invitation to **{receiverName}** to join {townName} has expired."
            await client.get_channel(invData["CHANNEL"]).send(embed=embed)
            os.remove(f"towninvites/{inv}.json")
        else:
            setInviteData(inv, invData)


async def inviteHandler(ctx, receiver):
    embed = makeEmbed()
    embed.color = discord.Color.red()
    playerID = str(ctx.author.id)
    if not isMayor(playerID):
        embed.description = "You do not own a town! Only mayors can invite players."
        await ctx.send(embed=embed)
        return
    receiverID = identify(receiver)
    if receiverID.startswith("ERROR"):
        embed.description = receiverID.replace("ERROR ", "")
        await ctx.send(embed=embed)
        return
    if getPlayerTown(receiverID) is not None:
        embed.description = f"{getFullName(receiverID)} is already in a town!"
        await ctx.send(embed=embed)
        return
    if receiverID + ".json" in os.listdir("towninvites"):
        invData = getInviteData(receiverID)
        invTown = getTownName(invData["TOWN"])
        embed.description = f"{getFullName(receiverID)} is already being invited to {invTown}!"
        await ctx.send(embed=embed)
        return
    townID = getPlayerTown(playerID)
    if getHouseForSale(townID) is None:
        embed.description = f"There are no houses for sale!\n\n Build a house using `-plot build house YX`, \nthen mark it for sale using `-plot forsale YX`\n where YX is the plot you'd like to use."
        await ctx.send(embed=embed)
        return
    with open("non-code/towninvite.json", "r") as read_file:
        newInv = json.load(read_file)
    sender = getFullName(playerID)
    receiver = getFullName(receiverID)
    townID = getPlayerTown(playerID)
    newInv["SENDER"] = playerID
    newInv["TOWN"] = townID
    newInv["CHANNEL"] = ctx.channel.id
    newInv["TTL"] = invTTL
    setInviteData(receiverID, newInv)
    embed.color = discord.Color.green()
    embed.description = f"""**{sender}** has invited **{receiver}** an invite to {getTownName(townID)}.\n\nDo `-town accept` to join, or `-town deny` to reject the invitation.
                        \n\nWARNING: The town mayor can potentially kick you at any time, so make sure they are someone you can trust!"""
    await ctx.send(embed=embed)


async def invDenyHandler(ctx):
    embed = makeEmbed()
    embed.color = discord.Color.red()
    playerID = str(ctx.author.id)
    if playerID + ".json" not in os.listdir("towninvites"):
        embed.description = "You don't have any incoming invites."
        await ctx.send(embed=embed)
        return
    os.remove(f"towninvites/{playerID}.json")
    embed.description = "Invite denied."
    embed.color = discord.Color.dark_gray()
    await ctx.send(embed=embed)
    return


async def invAcceptHandler(ctx):
    embed = makeEmbed()
    embed.color = discord.Color.red()
    playerID = str(ctx.author.id)
    if playerID + ".json" not in os.listdir("towninvites"):
        embed.description = "You don't have any incoming invites."
        await ctx.send(embed=embed)
        return
    invData = getInviteData(playerID)
    townID = invData["TOWN"]
    housePlot = getHouseForSale(townID)
    if housePlot is None:
        embed.description = "This town does not have a house for sale. Ask the mayor to put a house for sale, and invite you again."
        os.remove(f"towninvites/{playerID}.json")
        await ctx.send(embed=embed)
        return
    townData = getTownData(townID)
    townData["RESIDENTS"].append(playerID)
    townData["PLOTS"][housePlot]["OWNER"] = playerID
    townData["PLOTS"][housePlot]["PLOTTYPE"] = "HOUSE"
    setTownData(townID, townData)
    playerData = getPlayerData(playerID)
    playerData["PLOTS"] = 1
    playerData["TOWN"] = townID
    setPlayerData(playerID, playerData)
    embed.color = discord.Color.green()
    embed.description = f"You have successfully joined **{getTownName(townID)}**!"
    await ctx.send(embed=embed)
    os.remove(f"towninvites/{playerID}.json")



