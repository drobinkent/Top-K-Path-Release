import random as rnd

import numpy as np

import ConfigConst
import Testingconst as tstConst

def generateRandomProbeResult(allPortsAsList = [5,6,7,8], minLinkRate=0.4, maxLinkRate=0.9):
    totalNormalizedRate = len(allPortsAsList)
    newPortRateList = []
    onlyRatelist = []
    for i in range(0, len(allPortsAsList)):
        x = rnd.uniform(minLinkRate, maxLinkRate)
        x = round(x, 1)
        onlyRatelist.append(x)
        tple1 = (allPortsAsList[i], x)
        newPortRateList.append(tple1)
    newPortRateList.sort(key=lambda x: x[1], reverse=False)
    return newPortRateList, onlyRatelist


def printRandomProbeResults(randomProberesult):
    for i in range(0, len(randomProberesult)):
        print(randomProberesult[i])

def generateAndStoreRandomProbeResults(times):
    probeResultsAsList = []
    # timeAsList = []
    # for i in range(0, int(times/ConfigConst.MULTITENANCY_RATE_RECONFIGURATION_INTERVAL)):
    #     x = rnd.uniform(minLinkRate, maxLinkRate)

    allRateList = []
    for i in range(0, times):
        probeResult, onlyRateList = generateRandomProbeResult()
        for j in onlyRateList:
            allRateList.append(j)
        probeResultsAsList.append(probeResult)

    print(probeResultsAsList)
    print(np.average(allRateList))
    return probeResultsAsList
        #printRandomProbeResults(probeResultsAsList)

portRateConfigs = generateAndStoreRandomProbeResults(times=500) # for each 5 sec create a new config
# for i in range (0, len(portRateConfigs)):
#     print(portRateConfigs[i][0][0])  # this gives port
#     print(portRateConfigs[i][0][1]) # this gives rate
#     print("\n\n")

    #if any port have rate 0 that means the port will be deleted
