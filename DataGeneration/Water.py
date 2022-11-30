import json
from datetime import datetime as dt
from datetime import timedelta
from configuration import getStartDate, getEndDate

total_water = 0

def take_shower(time, file):
    # total water var and incremental var
    global total_water
    shower_gal_per_min = 2.5

    # adding initial value to csv
    file.write('Bathroom, Shower, ' + time.strftime(timeFormat) + ', ' + str(total_water) + ' gallons total,' + ' production\n') 

    # looping to update total water throught duration of shower
    for i in range(20):  # shower duration 10 mins
        time += timedelta(seconds=30)  # updating data every 30 seconds
        total_water += (shower_gal_per_min/2)  # updating water accordingly
        # adding to csv
        file.write('Bathroom, Shower, ' + time.strftime(timeFormat) + ', ' + str(total_water) + ' gallons total,' + ' production\n') 
    return time


def take_bath(time, file):
    # total water var and incremental var
    global total_water
    shower_gal_per_min = 2.5

    # adding initial value to csv
    file.write('\n')
    file.write('Bathroom, Bath, ' + time.strftime(timeFormat) + ', ' + str(total_water) + ' gallons total,' + ' production\n') 

    # looping to update total water throught duration of shower
    for i in range(24): # shower duration 10 mins
        time += timedelta(seconds=30)  # updating data every 30 seconds
        total_water += (shower_gal_per_min/2) # updating water accordingly
        # adding to csv
        file.write('Bathroom, Bath, ' + time.strftime(timeFormat) + ', ' + str(total_water) + ' gallons total,' + ' production\n') 
    return time


if __name__ == '__main__':

    f = open("data.csv", "w")
    timeFormat = "%m/%d/%Y %H:%M:%S"

    # start seven days in the past
    startTime = getStartDate()
    endTime = getEndDate()
    currentTime = startTime

    # looping through past 7 days
    while currentTime < endTime:
        # setting today to 7 days ago
        day = currentTime.weekday()
        # M - F
        if day in [0, 1, 2, 3, 4]:
            # taking a shower
            if (currentTime.hour in [8, 10]) and (currentTime.minute == 00):  # two times a day
                currentTime = take_shower(currentTime, f)
            # taking a bath
            if (currentTime.hour in [9, 11]) and (currentTime.minute == 00):  # two times a day
                currentTime = take_bath(currentTime, f)

        # S - S 
        if day in [5, 6]:
            # taking a shower
            if (currentTime.hour in [8, 10, 12]) and (currentTime.minute == 00):  # 3 times a day
                currentTime = take_shower(currentTime, f)
            # taking a bath
            if (currentTime.hour in [9, 11, 13]) and (currentTime.minute == 00):  # 3 times a day
                currentTime = take_bath(currentTime, f)
            
        currentTime += timedelta(seconds=1)
    f.close()

