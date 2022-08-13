import json
import os
import discord

from tbLib.townsData import *
from tbLib.tbutils import makeEmbed
from tbLib.playerData import *
from tbLib.identifier import *

invTTL = 150                                                                                                # TTL for the invites, which is how many seconds until invites expire


def getInviteData(invID):                                                                                   # gets invite data
    with open(f"towninvites/{invID}.json", "r") as read_file:
        return json.load(read_file)


def setInviteData(invID, invData):                                                                          # sets invite data
    with open(f"towninvites/{invID}.json", "w") as write_file:
        json.dump(invData, write_file)


async def deqTownTTLs(client, amount):                                                                      # since towns eventually expire, they have a ttl that decrements
    for inv in os.listdir("towninvites"):                                                                   # goes through every invite that currently exists
        inv = inv.replace(".json", "")
        invData = getInviteData(inv)
        invData["TTL"] -= amount                                                                            # decrements the ttl
        if invData["TTL"] <= 0:                                                                             # if ttl is expired, delete
            embed = makeEmbed()
            senderName = getFullName(invData["SENDER"])
            receiverName = getFullName(inv)
            townName = getTownName(invData["TOWN"])
            embed.description = f"**{senderName}**'s invitation to **{receiverName}** to join {townName} has expired."
            await client.get_channel(invData["CHANNEL"]).send(embed=embed)                                  # sends message in channel the invite was made in
            os.remove(f"towninvites/{inv}.json")                                                            # removes invite save data
        else:
            setInviteData(inv, invData)


async def inviteHandler(ctx, receiver):                                                                     # handles inviting players
    embed = makeEmbed()
    embed.color = discord.Color.red()
    playerID = str(ctx.author.id)
    if not isMayor(playerID):                                                                               # checks if the user is a mayor, only mayors can invite players
        embed.description = "You do not own a town! Only mayors can invite players."
        await ctx.send(embed=embed)
        return
    receiverID = identify(receiver)                                                                         # finds ID of the invite recipient
    if receiverID.startswith("ERROR"):                                                                      # if the ID starts with error, recipient doesn't exist
        embed.description = receiverID.replace("ERROR ", "")                                                # ID is replaced with error message, so print that
        await ctx.send(embed=embed)
        return
    if getPlayerTown(receiverID) is not None:                                                               # checks if the recipient is already in a town
        embed.description = f"{getFullName(receiverID)} is already in a town!"
        await ctx.send(embed=embed)
        return
    if receiverID + ".json" in os.listdir("towninvites"):                                                   # checks if the recipient is already being invited to a town
        invData = getInviteData(receiverID)
        invTown = getTownName(invData["TOWN"])
        embed.description = f"{getFullName(receiverID)} is already being invited to {invTown}!"
        await ctx.send(embed=embed)
        return
    townID = getPlayerTown(playerID)
    if getHouseForSale(townID) is None:                                                                     # checks if there is a house for sale that the user can move into
        embed.description = f"There are no houses for sale!\n\n Build a house using `-plot build house YX`, \nthen mark it for sale using `-plot forsale YX`\n where YX is the plot you'd like to use."
        await ctx.send(embed=embed)
        return
    with open("non-code/towninvite.json", "r") as read_file:
        newInv = json.load(read_file)
    sender = getFullName(playerID)                                                                          # initializes data for the invite
    receiver = getFullName(receiverID)
    townID = getPlayerTown(playerID)
    newInv["SENDER"] = playerID
    newInv["TOWN"] = townID
    newInv["CHANNEL"] = ctx.channel.id                                                                      # channel is specified in case an error message is required to be sent
    newInv["TTL"] = invTTL                                                                                  # ttl is set so the message can expire
    setInviteData(receiverID, newInv)                                                                       # sets invite data
    embed.color = discord.Color.green()
    embed.description = f"""**{sender}** has invited **{receiver}** an invite to {getTownName(townID)}.\n\nDo `-town accept` to join, or `-town deny` to reject the invitation.
                        \n\nWARNING: The town mayor can potentially kick you at any time, so make sure they are someone you can trust!"""
    await ctx.send(embed=embed)


async def invDenyHandler(ctx):                                                                              # handles denying invites
    embed = makeEmbed()
    embed.color = discord.Color.red()
    playerID = str(ctx.author.id)
    if playerID + ".json" not in os.listdir("towninvites"):                                                 # goes through all invites and sees if the user is currently invited
        embed.description = "You don't have any incoming invites."
        await ctx.send(embed=embed)
        return
    os.remove(f"towninvites/{playerID}.json")                                                               # removes the invite
    embed.description = "Invite denied."
    embed.color = discord.Color.dark_gray()
    await ctx.send(embed=embed)
    return


async def invAcceptHandler(ctx):                                                                            # handles accepting invites
    embed = makeEmbed()
    embed.color = discord.Color.red()
    playerID = str(ctx.author.id)
    if playerID + ".json" not in os.listdir("towninvites"):                                                 # goes through all invites and sees if user is currently invites
        embed.description = "You don't have any incoming invites."
        await ctx.send(embed=embed)
        return
    invData = getInviteData(playerID)                                                                       # gets invite data
    townID = invData["TOWN"]
    housePlot = getHouseForSale(townID)                                                                     # searches for an available house to give to the user
    if housePlot is None:                                                                                   # checks again if there is still an available house for sale
        embed.description = "This town does not have a house for sale. Ask the mayor to put a house for sale, and invite you again."
        os.remove(f"towninvites/{playerID}.json")                                                           # removes the invite
        await ctx.send(embed=embed)
        return
    townData = getTownData(townID)
    townData["RESIDENTS"].append(playerID)                                                                  # adds player to the town residents list
    townData["PLOTS"][housePlot]["OWNER"] = playerID                                                        # gives the house plot to the player
    townData["PLOTS"][housePlot]["PLOTTYPE"] = "HOUSE"
    setTownData(townID, townData)
    playerData = getPlayerData(playerID)
    playerData["PLOTS"] = 1                                                                                 # sets the player's plot count to 1
    playerData["TOWN"] = townID                                                                             # sets the player's town to the current town
    setPlayerData(playerID, playerData)
    embed.color = discord.Color.green()
    embed.description = f"You have successfully joined **{getTownName(townID)}**!"
    await ctx.send(embed=embed)
    os.remove(f"towninvites/{playerID}.json")



