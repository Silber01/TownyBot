from tbLib.towns import *


async def townCommandsHandler(ctx, args):
    argsCount = len(args)
    for i in range(argsCount):
        args[i] = args[i].lower()
    if argsCount == 0:
        await townsHelp(ctx)
        return
    if args[0] == "new":
        if argsCount == 1:
            await newTown(ctx)
        else:
            await newTown(ctx, args[1])
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

