from tbLib.towns import *
from tbLib.plots import *
from tbLib.towninvites import *


# handles the numerous subcommands for -town
async def townCommandsHandler(ctx, args, client):
    argsCount = len(args)                                                               # counts amount of arguments, not including -town itself
    if argsCount >= 1:
        if args[0].lower() not in ["new", "rename"]:                                    # for -town new and -town rename, the casing of the command matters. Otherwise, it does not matter
            for i in range(argsCount):
                args[i] = args[i].lower()
        else:
            args[0] = args[0].lower()                                                   # the subcommand directly after -town should always be lowercase
    if argsCount == 0:                                                                  # if no subcommand is given, assume -town info
        await townsHelp(ctx)
        return
    if args[0] in ["info", "stats"]:                                                    # town info, also accepts town stats
        if argsCount == 1:
            await townInfoHandler(ctx)                                                  # if there is no second argument, assume the player wants their own town. Handled by infoHandler
        else:
            await townInfoHandler(ctx, args[1])                                         # if there is a second argument, assume it is a town name
        return
    if args[0] == "rename":                                                             # handles renaming
        if argsCount == 1:                                                              # town rename subcommand needs a second argument, throws error if not present
            embed = makeEmbed()
            embed.color = discord.Color.red()
            embed.description = "Invalid syntax! Syntax is `-town rename <name>`."
            await ctx.send(embed=embed)
            return
        await renameHandler(ctx, args[1])
        return
    if args[0] == "new":                                                                # handles town new
        if argsCount == 1:
            await newTownHandler(ctx, client)
        else:
            await newTownHandler(ctx, client, args[1])                                  # if a second argument is given, assume it is the town name
        return
    if args[0] == "delete":                                                             # handles town delete
        await deleteTownHandler(ctx, client)
        return
    if args[0] == "map":                                                                # handles town map
        if argsCount == 1:
            await makeMapHandler(ctx)
        else:
            await makeMapHandler(ctx, args[1])                                          # if second argument is given, assume it is the town name
        return
    if args[0] == "ownedplots":                                                         # handles town ownedplots
        if argsCount == 1:
            await makeOwnerMapHandler(ctx)
        else:
            await makeOwnerMapHandler(ctx, args[1])                                     # if second argument is given, assume it is the player name
        return
    if args[0] == "forsale":                                                            # handles town forsale
        if argsCount == 1:
            await makeForSaleMapHandler(ctx)
        else:
            await makeForSaleMapHandler(ctx, args[1])                                   # if second argument is given, assume it is the town name
        return
    if args[0] == "invite":                                                             # handles town invite
        if argsCount != 2:                                                              # if a second argument isn't given, throw error
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-town invite <player>`"
            await ctx.send(embed=embed)
            return
        await inviteHandler(ctx, args[1])
        return
    if args[0] == "deny":                                                               # handles town deny, for invite request
        await invDenyHandler(ctx)
        return
    if args[0] == "accept":                                                             # handles town accept, for invite request
        await invAcceptHandler(ctx)
        return
    if args[0] == "leave":                                                              # handles town leave
        await leaveHandler(ctx, client)
        return
    if args[0] == "kick":                                                               # handles town kick
        if argsCount != 2:                                                              # if a second argument isn't given, throw error
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-town kick <player>`"
            await ctx.send(embed=embed)
            return
        await kickHandler(ctx, client, args[1])
        return
    if args[0] == "set":                                                                # handles set, which is itself a subcommand. Possible sets are plotprice and mayor
        if argsCount < 2:                                                               # if no arguments are given, gives invalid syntax error and provides possible commands
            embed = makeEmbed()
            embed.description = """Invalid syntax! Possible commands for `-town set` are 
                                `-town set mayor <new mayor>`, or `-town set plotprice <plot price>`."""
            await ctx.send(embed=embed)
        if args[1] not in ["plotprice", "mayor"]:                                       # if arguments are invalid, give same error as above
            embed = makeEmbed()
            embed.description = """Invalid syntax! Possible commands for `-town set` are 
                                `-town set mayor <new mayor>`, or `-town set plotprice <plot price>`."""
            await ctx.send(embed=embed)
            return
        if args[1] == "plotprice":                                                      # sets price to buy a plot from the town
            if argsCount != 3:                                                          # for plotprice, checks if amount is given
                embed = makeEmbed()
                embed.description = "Invalid syntax! Syntax is `-plot set plotprice <plot price>`."
                await ctx.send(embed=embed)
                return
            await plotPriceHandler(ctx, args[2])
            return
        if args[1] == "mayor":                                                          # sets new mayor for town
            if argsCount != 3:                                                          # for mayor, checks if new mayor name is given
                embed = makeEmbed()
                embed.description = "Invalid syntax! Syntax is `-plot set mayor <new mayor>`."
                await ctx.send(embed=embed)
                return
            await newMayorHandler(ctx, args[2], client)
        return
    if args[0] == "list":                                                               # handles town list
        if argsCount == 1:
            await townListHandler(ctx)
            return
        await townListHandler(ctx, args[1])                                             # if argument given, assumes it's the page number of the town list
        return
    if args[0] == "buy":                                                                # other name for -plot annex
        if argsCount != 2:                                                              # if second argument is not given, throw error
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot annex YX`, i.e. `-plot annex C4`."
            await ctx.send(embed=embed)
            return
        await annexHandler(ctx, args[1], client)
        return
    if args[0] in ["annex", "build", "clear"]:                                          # for some plot commands, sends it over to plot commands handler in case user made mistake
        await plotCommandsHandler(ctx, args, client)
        return
    embed = makeEmbed()                                                                 # if none of the commands occured, then the user put in an invalid command. Throw error
    embed.color = discord.Color.red()
    embed.description = "Invalid town command! Do `-help towns` to see a list of towny commands"
    await ctx.send(embed=embed)


# handles subcommands for plot
async def plotCommandsHandler(ctx, args, client):
    argsCount = len(args)                                                               # counts how many arguments are after -plot
    args[0] = args[0].lower()
    if args[0] == "info":                                                               # handles plot info
        if argsCount != 2:                                                              # if no plot is given, throw syntax error
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot info YX`, i.e. `-plot info C4`."
            await ctx.send(embed=embed)
            return
        await plotInfo(ctx, args[1])
        return
    if args[0] == "annex":                                                              # handles annexing plot
        if argsCount != 2:                                                              # if no plot is given, throw syntax error
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot annex YX`, i.e. `-plot annex C4`."
            await ctx.send(embed=embed)
            return
        await annexHandler(ctx, args[1], client)
        return
    if args[0] == "abandon":                                                            # handles abandoning a plot
        if argsCount != 2:                                                              # if no plot is given, throw syntax error
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot abandon YX`, i.e. `-plot abandon C4`."
            await ctx.send(embed=embed)
            return
        await abandonHandler(ctx, client, args[1])
        return
    if args[0] == "build":                                                              # handles building structures on a plot
        if argsCount != 3:                                                              # build needs a plot and a structure arg. If not given, throw syntax error
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot build <structure> YX`, i.e. `-plot build mine C4`."
            await ctx.send(embed=embed)
            return
        await buildHandler(ctx, args[2], args[1], client)
        return
    if args[0] == "clear":                                                              # handles clearing structures from a plot
        if argsCount != 2:                                                              # if no plot is given, throw syntax error
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot info YX`, i.e. `-plot info C4`."
            await ctx.send(embed=embed)
            return
        await clearHandler(ctx, args[1])
        return
    if args[0] == "forsale":                                                            # handles marking plots for sale
        if argsCount != 2:                                                              # if no plot is given, throw syntax error
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot forsale YX`, i.e. `-plot forsale C4`."
            await ctx.send(embed=embed)
            return
        await forsaleHandler(ctx, args[1])
        return
    if args[0] == "notforsale":                                                         # handles marking a plot not for sale
        if argsCount != 2:                                                              # if no plot is given, throw syntax error
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot notforsale YX`, i.e. `-plot notforsale C4`."
            await ctx.send(embed=embed)
            return
        await notforsaleHandler(ctx, args[1])
        return
    if args[0] == "buy":                                                                # handles buying a plot that is for sale
        if argsCount != 2:                                                              # if no plot is given, throw syntax error
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot buy YX`, i.e. `-plot buy C4`."
            await ctx.send(embed=embed)
            return
        await buyHandler(ctx, args[1])
        return
    if args[0] == "unclaim":                                                            # handles unclaiming a plot
        if argsCount != 2:                                                              # if no plot is given, throw syntax error
            embed = makeEmbed()
            embed.description = "Invalid syntax! Syntax is `-plot unclaim YX`, i.e. `-plot unclaim C4`."
            await ctx.send(embed=embed)
            return
        await unclaimHandler(ctx, args[1])
        return
    if args[0] in ["map", "ownedplots"]:                                                # handles some town commands, and sends it to the town commands handler in case user accidentally uses plot
        await townCommandsHandler(ctx, args, client)
        return
    embed = makeEmbed()                                                                 # if no commands were called, the command was invalid
    embed.color = discord.Color.red()
    embed.description = "Invalid town command! Do `-help towns` to see a list of towny commands"
    await ctx.send(embed=embed)
