import json

from datetime import timedelta
from values import getStartDate, getEndDate
# import pandas as pd

def DoInternalTempSequence(external, internal, time, file):
    # external temp 10 above internal
    external += 10

    # Internal Temp, External Temp, time record, prod
    file.write(time.strftime(timeFormat) + ',' + str(round(internal, 2)) + ',production\n')

    # + 10 deg difference means + 2 deg internal 
    if external >= internal + 10:
        for minute in range(0, 60):  # Traverse every minute to show 2 deg change/time
            time += timedelta(minutes=1)
            # if minute == 59:
            #     internal += 2/60 + .000000002
            internal += 2/60
            file.write(time.strftime(timeFormat) + ',' + str(round(internal, 2)) + ',production\n')

    # external temp 10 below internal
    external = 62

    # Internal Temp, External Temp, time record, prod
    file.write(time.strftime(timeFormat) + ',' + str(round(internal, 2)) + ',production\n')

    # - 10 deg difference means - 2 deg internal 
    if external >= internal - 10:
        for minute in range(0, 60):  # Traverse every minute to show 2 deg change/time
            time += timedelta(minutes=1)
            internal -= 2/60
            file.write(time.strftime(timeFormat) + ',' + str(round(internal, 2)) + ',production\n')

    return time

if __name__ == '__main__':
    f = open("data.csv", "w")
    timeFormat = "%m/%d/%Y %H:%M:%S"
    startTime = getStartDate()
    endTime = getEndDate()
    currentTime = startTime

    # test numbers for now, will later implement externalTemp functionality from MMD
    externalTemp = 70
    internalTemp = 70

    while currentTime < endTime:
        currentTime = DoInternalTempSequence(externalTemp, internalTemp, currentTime, f)

    f.close()