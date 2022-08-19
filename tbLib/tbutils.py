import asyncio
import discord


# returns embed with default settings. Done this way to easily make edits to default embed properties
def makeEmbed():
    return discord.Embed(title="TownyBot")


# warns a user by giving a message they have to say to confirm what they want to do. Returns whether or not player has confirmed
async def warnUser(ctx, client, warningMsg, cancelMsg, timeoutMsg, timer, confirmMsg):
    embed = makeEmbed()
    embed.description = warningMsg
    embed.set_footer(text=f"This request will time out in {timer} seconds.")
    await ctx.send(embed=embed)

    def check(m):                                                               # determines what criteria to hit to stop waiting for response
        return m.author == ctx.author

    try:
        msg = await client.wait_for("message", check=check, timeout=timer)
    except asyncio.TimeoutError:                                                # what to do if time runs out
        embed.description = timeoutMsg
        await ctx.send(embed=embed)
        return False
    if msg.content.upper() != confirmMsg.upper():                               # what to do if response is invalid
        embed.description = cancelMsg
        await ctx.send(embed=embed)
        return False
    return True


# given a number, low, and high, determines if number is valid, not a number, too low, or too high
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


def formatNum(number):
    return "{:,}".format(int(number))
