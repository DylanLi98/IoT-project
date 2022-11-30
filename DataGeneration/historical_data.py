import datetime
import bisect
import argparse
from core import *

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--no-sql", help="disable SQL logging", action="store_true")
	args = parser.parse_args()
	f = open("data.csv", "w")

	# start seven days in the past
	startTime = datetime.datetime.now() - datetime.timedelta(days=62)
	endTime = datetime.datetime.now()
	currentTime = startTime
	lastMinute = startTime.minute
	
	queuedEvents = []

	def queueEvent(lam, offTime):
		bisect.insort(queuedEvents, Event(offTime, lam), key = lambda x: x.getTimestamp())
	
	iot_house = SmartHome()
	iot_house.addDevice(Light(name = "Ceiling Light", location = "Bedroom", csvfile = f))
	iot_house.addDevice(Window(name = "Stove Window", location = "Kitchen", csvfile = f))
	iot_house.addDevice(Window(name = "Sink Window", location = "Kitchen", csvfile = f))
	iot_house.addDevice(Door(name = "Front Door", location = "Living Room", csvfile = f))
	iot_house.addSensor(InternalThermostatSensor(name = "Internal Temperature", location = "Hallway", csvfile = f))
	iot_house.getSensorByClass(InternalThermostatSensor).setValue(70.0)
	iot_house.addSensor(ExternalThermostatSensor(name = "External Temperature", location = "Porch", csvfile = f))
	iot_house.getSensorByClass(ExternalThermostatSensor).setValue(30.0)
	iot_house.addDevice(Hvac(name = "HVAC", location = "Basement", csvfile = f))
	iot_house.addDevice(Shower(name = "Shower", location = "Bathroom", csvfile = f))
	iot_house.addDevice(Bathtub(name = "Bathtub", location = "Bathroom", csvfile = f))

	# Generate historical data for the last 7 days
	while currentTime < endTime:
		day = currentTime.weekday()

		# Every second:
		# Run queued events:
		for idx, event in enumerate(queuedEvents):
			if event.time > currentTime:
				break
			if event.fired:
				print(f"Event {event} already fired!")
				print(datetime.datetime.now())
			event.invoke()
			del queuedEvents[idx]

		# Every minute:
		if currentTime.minute != lastMinute:
			lastMinute = currentTime.minute
			iot_house.log(time = currentTime, no_sql = args.no_sql)

			# WINDOWS
			# ALL WEEK
			if (currentTime.hour in [7, 1, 17] and (currentTime.minute == 30)):
				window1 = iot_house.getDeviceByClass(Window, 0)
				window2 = iot_house.getDeviceByClass(Window, 1)
				window1.toggle(time = currentTime)
				offTime = currentTime + datetime.timedelta(minutes = 15)
				queueEvent(lambda: window1.toggle(time = offTime), offTime)
				window2Time = currentTime + datetime.timedelta(minutes = 5)
				queueEvent(lambda: window2.toggle(time = window2Time), window2Time)
				off2Time = window2Time + datetime.timedelta(minutes = 5)
				queueEvent(lambda: window2.toggle(time = off2Time), off2Time)

			# M - F
			if day <= 4:
				# LIGHTS
				if (currentTime.hour in [8, 9, 17, 18, 19, 20, 21, 22]) and (currentTime.minute == 00): # 8 times a day                
					lightbulb1 = iot_house.getDeviceByClass(Light, 0)
					lightbulb1.actuate(True, time = currentTime)
					offTime = currentTime + datetime.timedelta(minutes = 30)
					queueEvent(lambda: lightbulb1.actuate(False, time = offTime), offTime)
				# DOORS
				if (currentTime.hour in [8, 18]) and (currentTime.minute in [5, 10, 15, 20, 30, 40, 45, 50]):
					frontdoor = iot_house.getDeviceByClass(Door, 0)
					frontdoor.actuate(True, time = currentTime)
					offTime = currentTime + datetime.timedelta(seconds = 30)
					queueEvent(lambda: frontdoor.actuate(False, time = offTime), offTime)
				# taking a shower
				if (currentTime.hour in [8, 10]) and (currentTime.minute == 00):  # two times a day
					shower = iot_house.getDeviceByClass(Shower, 0)
					shower.actuate(True, time = currentTime)
					offTime = currentTime + datetime.timedelta(minutes = 10)
					queueEvent(lambda: shower.actuate(False, time = offTime), offTime)
				# taking a bath
				if (currentTime.hour in [9, 11]) and (currentTime.minute == 00):  # two times a day
					bathtub = iot_house.getDeviceByClass(Bathtub, 0)
					bathtub.actuate(True, time = currentTime)
					offTime = currentTime + datetime.timedelta(minutes = 10)
					queueEvent(lambda: bathtub.actuate(False, time = offTime), offTime)

			# S - S 
			else:
				if (currentTime.hour in [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]) and (currentTime.minute == 00): # 14 times a day
					lightbulb1 = iot_house.getDeviceByClass(Light, 0)
					lightbulb1.actuate(True, time = currentTime)
					offTime = currentTime + datetime.timedelta(minutes = 30)
					queueEvent(lambda: lightbulb1.actuate(False, time = offTime), offTime)
				if (currentTime.hour in [8, 11, 14, 18]) and (currentTime.minute in [5, 10, 15, 20, 30, 40, 45, 50]):
					frontdoor = iot_house.getDeviceByClass(Door, 0)
					frontdoor.actuate(True, time = currentTime)
					offTime = currentTime + datetime.timedelta(seconds = 30)
					queueEvent(lambda: frontdoor.actuate(False, time = offTime), offTime)
				# taking a shower
				if (currentTime.hour in [8, 10, 12]) and (currentTime.minute == 00):  # 3 times a day
					shower = iot_house.getDeviceByClass(Shower, 0)
					shower.actuate(True, time = currentTime)
					offTime = currentTime + datetime.timedelta(minutes = 10)
					queueEvent(lambda: shower.actuate(False, time = offTime), offTime)
				# taking a bath
				if (currentTime.hour in [9, 11, 13]) and (currentTime.minute == 00):  # 3 times a day
					bathtub = iot_house.getDeviceByClass(Bathtub, 0)
					bathtub.actuate(True, time = currentTime)
					offTime = currentTime + datetime.timedelta(minutes = 10)
					queueEvent(lambda: bathtub.actuate(False, time = offTime), offTime)

		for device in iot_house.getDevices():
			device.elapseTime(1, currentTime)
		iot_house.updateTemperature(1)
		currentTime += datetime.timedelta(seconds=1)
	f.close()
