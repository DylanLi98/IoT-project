import json
from datetime import datetime as dt
from datetime import timedelta

total_kwatth = 0
total_electricityCost = 0

# parmas: used hour
# return: electricty cost for certain used hour
def useLightbulb(time, file):
    global total_kwatth
    global total_electricityCost
    khwatt = 0.06 # All Light Bulbs are 60 watt

    # adding initial value to csv
    file.write('Bedroom, Lightbulb, ' + time.strftime(timeFormat) + ', ' + str(total_kwatth) + ' kwatth total,' + str(total_electricityCost) + ' electricity Cost total,' + ' production\n') 

    # looping to update total kwatt 
    for i in range(20): # duration 30 mins
        time += timedelta(minutes=6)  # updating data every 6 mins
        total_kwatth += (khwatt * 0.1) # updating kwatth accordingly
        total_kwatth = round(total_kwatth, 4)
        total_electricityCost += (0.12 * total_kwatth)  # Electricity Cost: $0.12 per kWh
        total_electricityCost = round(total_electricityCost, 4)
        # adding to csv
        file.write('Bedroom, Lightbulb, ' + time.strftime(timeFormat) + ', ' + str(total_kwatth) + ' kwatth total,' + str(total_electricityCost) + ' electricity Cost total,' + ' production\n') 
    return time

if __name__ == '__main__':

    f = open("data.csv", "w")
    timeFormat = "%m/%d/%Y %H:%M:%S"

    # start seven days in the past
    startTime = dt.now() - timedelta(days=7)
    endTime = dt.now()
    currentTime = startTime

    # loopng through past 7 days
    while currentTime < endTime:
        
        # setting today to 7 days ago
        day = currentTime.weekday()


        # M - F
        if day in [0,1,2,3,4]:
            if (currentTime.hour in [8, 9, 17, 18, 19, 20, 21, 22]) and (currentTime.minute == 00): # 8 times a day
                currentTime = useLightbulb(currentTime, f)
       
 
        # S - S 
        if day in [5,6]:
            if (currentTime.hour in [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]) and (currentTime.minute == 00): # 14 times a day
                currentTime = useLightbulb(currentTime, f)

        currentTime += timedelta(seconds=1)
    f.close()

