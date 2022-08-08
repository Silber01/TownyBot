from tbLib.towns import *
from tbLib.plots import *
from tbLib.towninvites import *

async def townCommandsHandler(ctx, args, client):
    argsCount = len(args)
    if argsCount >= 1:
        if args[0].lower() not in ["new", "rename"]:
            for i in range(argsCount):
                args[i] = args[i].lower()
        else:
            args[0] = args[0].lower()
    if argsCount == 0:
        await townsHelp(ctx)
        return
    if args[0] == "info":
        if argsCount == 1:
            await townInfoHandler(ctx)
        else:
            await townInfoHandler(ctx, args[1])
        return
    if args[0] == "rename":
        if argsCount == 1:
            embed = makeEmbed()
            embed.color = discord.Color.red()
            embed.description = "Invalid syntax! Syntax is `-town rename <name>`."
            await ctx.send(embed=embed)
            return
        await renameHandler(ctx, args[1])
        return
    if args[0] == "new":
        if argsCount == 1:
            await newTownHandler(ctx, client)
        else:
            await newTownHandler(ctx, client, args[1])
        return
    if args[0] == "delete":
        await deleteTownHandler(ctx, client)
        return
    if args[0] == "map":
        if argsCount == 1:
            await makeMapHandler(ctx)
        else:
            await makeMapHandler(ctx, args[1])
        return
    if args[0] == "ownedplots":
        if argsCount == 1:
            await makeOwnerMapHandler(ctx)
        else:
            await makeOwnerMapHandler(ctx, args[1])
        return
    if args[0] == "forsale":
        if argsCount == 1:
            await makeForSaleMapHandler(ctx)
        else:
            await makeForSaleMapHandler(ctx, args[1])
        return
    if args[0] == "invite":
        if argsCount != 2:
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-town invite <player>`"
            await ctx.send(embed=embed)
            return
        await inviteHandler(ctx, args[1])
        return
    if args[0] == "deny":
        await invDenyHandler(ctx)
    if args[0] == "accept":
        await invAcceptHandler(ctx)
    if args[0] == "leave":
        await leaveHandler(ctx, client)
    if args[0] == "kick":
        if argsCount != 2:
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-town kick <player>`"
            await ctx.send(embed=embed)
            return
        await kickHandler(ctx, client, args[1])
    if args[0] == "set":
        if argsCount < 2:
            embed = makeEmbed()
            embed.description = """Invalid syntax! Possible commands for `-town set` are 
                                `-town set mayor <new mayor>`, or `-town set plotprice <plot price>`."""
            await ctx.send(embed=embed)
        if args[1] not in ["plotprice", "mayor"]:
            embed = makeEmbed()
            embed.description = """Invalid syntax! Possible commands for `-town set` are 
                                           `-town set mayor <new mayor>`, or `-town set plotprice <plot price>`."""
            await ctx.send(embed=embed)
        if args[1] == "plotprice":
            if argsCount != 3:
                embed = makeEmbed()
                embed.description = "Invalid syntax! Syntax is `-plot set plotprice <plot price>`."
                await ctx.send(embed=embed)
                return
            await plotPriceHandler(ctx, args[2])
        if args[1] == "mayor":
            if argsCount != 3:
                embed = makeEmbed()
                embed.description = "Invalid syntax! Syntax is `-plot set mayor <new mayor>`."
                await ctx.send(embed=embed)
                return
            await newMayorHandler(ctx, args[2], client)
    if args[0] == "list":
        if argsCount == 1:
            await townListHandler(ctx)
            return
        await townListHandler(ctx, args[1])
        return
    if args[0] == "buy":
        if argsCount != 2:
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot annex YX`, i.e. `-plot annex C4`."
            await ctx.send(embed=embed)
            return
        await annexHandler(ctx, args[1], client)
        return
    if args[0] in ["annex", "build", "clear"]:
        await plotCommandsHandler(ctx, args, client)
        return


async def plotCommandsHandler(ctx, args, client):
    argsCount = len(args)
    if args[0] == "info":
        if argsCount != 2:
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot info YX`, i.e. `-plot info C4`."
            await ctx.send(embed=embed)
            return
        await plotInfo(ctx, args[1])
        return
    if args[0] == "annex":
        if argsCount != 2:
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot annex YX`, i.e. `-plot annex C4`."
            await ctx.send(embed=embed)
            return
        await annexHandler(ctx, args[1], client)
        return
    if args[0] == "abandon":
        if argsCount != 2:
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot abandon YX`, i.e. `-plot abandon C4`."
            await ctx.send(embed=embed)
            return
        await abandonHandler(ctx, client, args[1])
    if args[0] == "build":
        if argsCount != 3:
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot build <structure> YX`, i.e. `-plot build mine C4`."
            await ctx.send(embed=embed)
            return
        await buildHandler(ctx, args[2], args[1], client)
        return
    if args[0] == "clear":
        if argsCount != 2:
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot info YX`, i.e. `-plot info C4`."
            await ctx.send(embed=embed)
            return
        await clearHandler(ctx, args[1])
        return
    if args[0] == "forsale":
        if argsCount != 2:
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot forsale YX`, i.e. `-plot forsale C4`."
            await ctx.send(embed=embed)
            return
        await forsaleHandler(ctx, args[1])
        return
    if args[0] == "notforsale":
        if argsCount != 2:
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot notforsale YX`, i.e. `-plot notforsale C4`."
            await ctx.send(embed=embed)
            return
        await notforsaleHandler(ctx, args[1])
        return
    if args[0] == "buy":
        if argsCount != 2:
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot buy YX`, i.e. `-plot buy C4`."
            await ctx.send(embed=embed)
            return
        await buyHandler(ctx, args[1])
        return
    if args[0] == "unclaim":
        if argsCount != 2:
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot unclaim YX`, i.e. `-plot unclaim C4`."
            await ctx.send(embed=embed)
            return
        await unclaimHandler(ctx, args[1])
    if args[0] in ["map", "ownedplots"]:
        await townCommandsHandler(ctx, args, client)
        return
