import random


def validRemove(plotList: dict):
    firstPlot = random.choice(list(plotList))
    floodFill(plotList, firstPlot)
    for plot in plotList:
        if plotList[plot] == "UNMARKED":
            return False
    return True


def floodFill(plotList: dict, plot):
    if plotList[plot] == "MARKED":
        return
    plotList[plot] = "MARKED"
    Y = plot[0]
    X = plot[1]
    left = chr(ord(Y) - 1) + X
    if left in plotList:
        floodFill(plotList, left)
    right = chr(ord(Y) + 1) + X
    if right in plotList:
        floodFill(plotList, right)
    up = Y + chr(ord(X) - 1)
    if up in plotList:
        floodFill(plotList, up)
    down = Y + chr(ord(X) + 1)
    if down in plotList:
        floodFill(plotList, down)


def makePlotDict(plotList):
    plotDict = {}
    for plot in plotList:
        plotDict[plot] = "UNMARKED"
    return plotDict

def canRemovePlot(plotsData, plot):
    plotList = []
    for plotName in plotsData:
        plotList.append(plotName)
    plotList.remove(plot)
    plotDict = makePlotDict(plotList)
    return validRemove(plotDict)
