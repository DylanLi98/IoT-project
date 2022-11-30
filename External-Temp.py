from datetime import datetime as dt
from datetime import timedelta
from this import d
from urllib import response
import requests
# API info
key = "6beea754f0e594a259eba6d1babe6188"
city = "Birmingham"
lat= "33.5207"
lon = "-86.8025"
cityCode = "4049979"

#  ----------------Helper methods-------

# this method convert the temperatur(kelvin) from the API into fahrenheit
def kelvin_to_celcius_fahrenheit(kelvin):
    celcius = kelvin - 273.15
    fahrenheit = celcius * (9/5) + 32
    result = round(fahrenheit, 2)
    return result

# this method takes a value, the end of the first iteration and create a new range
def generate_start_date(value):
    days = timedelta(value)
    starttime = str(dt.now() - days)
    return starttime

# This method take the start and the end, and return a json response from the API in that interval
def getAPI_data(start, end):
    url = f"http://history.openweathermap.org/data/2.5/history/city?lat={lat}&lon={lon}&type=hour&start={start}&end={end}&appid={key}"
    return requests.get(url).json()

#This method take the start time and compute the end for the next iteration
def computeEndTime(startTime):
    return (7 * 24 * 3600) + startTime

# This function out put the temperature and the time for each iteration
# It is an important method
def computeTemperature(list, end, file):
    for i in range(len(list)):
        delta = 0
        temp = list[i]['main']['temp']
        fahrenheit = kelvin_to_celcius_fahrenheit(temp)
        dt_time = list[i]['dt']
        file.write('External Temperature, Temperature,' + str(dt.fromtimestamp(dt_time)) + ','+ str(fahrenheit)+ '°F ,production\n')
        # print(f"Temperature: {fahrenheit: .2f}°F date: {dt.fromtimestamp(dt_time)}")
        # add delta calculation
        temp_Inseconds = temp
        minuteStamp = dt_time
        secondFahrenheit = 0
        if i > 0:
            delta = (temp - list[i-1]['main']['temp']) / 60
        else:
            delta = temp / 60
        
        for j in range(60): # You can change 60 to 3600 to get for displaying in seconds
            temp_Inseconds += delta 
            minuteStamp += 60 + 1
            secondFahrenheit = kelvin_to_celcius_fahrenheit(temp_Inseconds)
            file.write('External Temperature, Temperature,' + str(dt.fromtimestamp(minuteStamp)) + ',' + str(secondFahrenheit) + '°F ,production\n')
            # print(f"Temperature: {secondFahrenheit: .2f}°F date: {dt.fromtimestamp(minuteStamp)}")
        if end == int(dt.timestamp(dt.now())):
            break

# Compute initial start and end
days_ago = (dt.now()- timedelta(30))
start = int(dt.timestamp(days_ago))
end = computeEndTime(start)
f = open("External-Temperature.csv", "w")

# This is where all the magics are put together
while start <= int(dt.timestamp(dt.now())):
    result = getAPI_data(str(start), str(end))
    list = result['list']
    computeTemperature(list, end, f)
    start = end
    end = computeEndTime(start)