import random


def validRemove(plotList: dict):                    # checks if any of the plots have been unmarked, meaning that the flood fill
    firstPlot = random.choice(list(plotList))       # did not reach all plots, which indicates the plot remove is invalid
    floodFill(plotList, firstPlot)
    for plot in plotList:
        if plotList[plot] == "UNMARKED":
            return False
    return True


def floodFill(plotList: dict, plot):                # recursively flood fills a map
    if plotList[plot] == "MARKED":
        return
    plotList[plot] = "MARKED"
    Y = plot[0]
    X = plot[1]
    left = chr(ord(Y) - 1) + X                      # bit manipulates the ascii code of the coordinate to reduce y value by 1
    if left in plotList:                            # if the resulting coordinate is part of the map, flood fill from that coordinate
        floodFill(plotList, left)
    right = chr(ord(Y) + 1) + X                     # repeat the same process as above for right, up, and down
    if right in plotList:
        floodFill(plotList, right)
    up = Y + chr(ord(X) - 1)
    if up in plotList:
        floodFill(plotList, up)
    down = Y + chr(ord(X) + 1)
    if down in plotList:
        floodFill(plotList, down)


def makePlotDict(plotList):                         # converts the plot list into a dictionary, all labeled "UNMARKED"
    plotDict = {}
    for plot in plotList:
        plotDict[plot] = "UNMARKED"
    return plotDict


# checks if removing a plot will cause the town to split apart.
# does this by removing the plot, then flodd filling a random plot to see if it reaches all plots.
# if it does not reach all plots, then the plot removal split the town apart.
def canRemovePlot(plotsData, plot):
    plotList = []
    for plotName in plotsData:                      # puts all plot data into a list
        plotList.append(plotName)
    plotList.remove(plot)                           # removes the plot that the player wants to remove
    plotDict = makePlotDict(plotList)               # converts list to dict
    return validRemove(plotDict)                    # uses new dict with other functions to see if flood fill is valid
