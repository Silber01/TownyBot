from tbLib.towns import *
from tbLib.plots import *

async def townCommandsHandler(ctx, args, client):
    argsCount = len(args)
    for i in range(argsCount):
        args[i] = args[i].lower()
    if argsCount == 0:
        await townsHelp(ctx)
        return
    if args[0] == "info":
        if argsCount == 1:
            await townInfoHandler(ctx)
        else:
            await townInfoHandler(ctx, args[1])
        return
    if args[0] == "new":
        if argsCount == 1:
            await newTownHandler(ctx)
        else:
            await newTownHandler(ctx, args[1])
        return
    if args[0] == "delete":
        await deleteTownHandler(ctx, client)
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
    if args[0] == "annex":
        if argsCount != 2:
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot annex YX`, i.e. `-plot annex C4`."
            await ctx.send(embed=embed)
            return
        await annexHandler(ctx, args[1], client)


async def plotCommandsHandler(ctx, args, client):
    argsCount = len(args)
    if args[0] == "info":
        if argsCount != 2:
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot info YX`, i.e. `-plot info C4`."
            await ctx.send(embed=embed)
            return
        await plotInfo(ctx, args[1])
    if args[0] == "annex":
        if argsCount != 2:
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot annex YX`, i.e. `-plot annex C4`."
            await ctx.send(embed=embed)
            return
        await annexHandler(ctx, args[1], client)
    if args[0] == "build":
        if argsCount != 3:
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot build <structure> YX`, i.e. `-plot build mine C4`."
            await ctx.send(embed=embed)
            return
        await buildHandler(ctx, args[2], args[1], client)
    if args[0] == "clear":
        if argsCount != 2:
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot info YX`, i.e. `-plot info C4`."


