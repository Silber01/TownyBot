from tbLib.towns import *
from tbLib.plots import *


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
            await newTownHandler(ctx)
        else:
            await newTownHandler(ctx, args[1])
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
    if args[0] in ["map", "ownedplots"]:
        await townCommandsHandler(ctx, args, client)
        return
