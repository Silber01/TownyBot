from tbLib.makeEmbed import makeEmbed
import asyncio


async def warnUser(ctx, client, warningMsg, cancelMsg, timeoutMsg, timer, confirmMsg):
    embed = makeEmbed()
    embed.description = warningMsg
    embed.set_footer(text=f"This request will time out in {timer} seconds.")
    await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author

    try:
        msg = await client.wait_for("message", check=check, timeout=timer)
    except asyncio.TimeoutError:
        embed.description = timeoutMsg
        await ctx.send(embed=embed)
        return False
    if msg.content.upper() != confirmMsg.upper():
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
