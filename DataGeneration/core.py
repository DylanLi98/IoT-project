import datetime
import warnings
import psycopg2
import socket

# copied from config.py; todo move somewhere secure
DBNAME = "Team2DB"
DBUSER = "Team2"
DBPASS = "team2"
DBHOST = "138.26.48.83"


timeFormat = "%Y-%m-%d %H:%M:%S"

isProduction = True

dbconn = psycopg2.connect(dbname = DBNAME, user = DBUSER, password = DBPASS, host = DBHOST)

class SmartHome(object):
	def __init__(self):
		self.devices = []
		self.devices_by_class = {}
		self.sensors = []
		self.sensors_by_class = {}

	def addDevice(self, device):
		device.house = self
		self.devices.append(device)
		if type(device) not in self.devices_by_class:
			self.devices_by_class[type(device)] = []
		self.devices_by_class[type(device)].append(device)
	def getDevices(self):
		return self.devices[:]
	def getDevicesByClass(self, device_class):
		if device_class not in self.devices_by_class:
			return []
		return self.devices_by_class[device_class][:]
	def getDeviceByClass(self, device_class, i = 0):
		device_list = self.getDevicesByClass(device_class)
		if len(device_list) <= i:
			return None
		return device_list[i]

	def addSensor(self, sensor):
		sensor.house = self
		self.sensors.append(sensor)
		if type(sensor) not in self.sensors_by_class:
			self.sensors_by_class[type(sensor)] = []
		self.sensors_by_class[type(sensor)].append(sensor)
	def getSensors(self):
		return self.sensors[:]
	def getSensorsByClass(self, sensor_class):
		if sensor_class not in self.sensors_by_class:
			return []
		return self.sensors_by_class[sensor_class][:]
	def getSensorByClass(self, sensor_class, i = 0):
		sensors = self.getSensorsByClass(sensor_class)
		if len(sensors) <= i:
			return None
		return sensors[i]
	
	def getTemperatureChange(self):
		"""Returns the temperature change per second in Fahrenheit."""
		doorOpen = False
		windowOpen = False
		externalTemp = self.getSensorByClass(ExternalThermostatSensor).getValue()
		internalTemp = self.getSensorByClass(InternalThermostatSensor).getValue()
		for door in self.getDevicesByClass(Door):
			if door.state:
				doorOpen = True
				break
		for window in self.getDevicesByClass(Window):
			if window.state:
				windowOpen = True
		temperatureChange = 0 # Change per 10F difference between external and internal temp
		if not doorOpen and not windowOpen:
			temperatureChange = 2/60/60 # 2F per hour, in seconds
		else:
			if doorOpen:
				temperatureChange += (2/5)/60 # 2F per 5 minutes, in seconds
			if windowOpen:
				temperatureChange += (1/5)/60 # 1F per 5 minutes, in seconds
		return (externalTemp - internalTemp) / 10 * temperatureChange
	
	def updateTemperature(self, secondsElapsed):
		temperatureChange = self.getTemperatureChange() * secondsElapsed
		self.getSensorByClass(InternalThermostatSensor).addValue(temperatureChange)
	
	def log(self, csvfile = None, time = None, no_sql = False):
		for device in self.getDevices():
			device.log(csvfile = csvfile, time = time, no_sql = no_sql)
		for sensor in self.getSensors():
			sensor.log(csvfile = csvfile, time = time, no_sql = no_sql)
		dbconn.commit()

class LocatedObject(object):
	def __init__(self, name, location = None, parent = None, **kwargs):
		super().__init__(**kwargs)
		self.name = name
		self.location = location
		self.parent = parent
		self.house = None
		if location is None and parent is None:
			raise ValueError("LocatedObject missing both location and parent (must have one!)")
	def SetLocation(self, newLocation):
		if self.parent is not None:
			warnings.warn("Attempted to set location of LocatedObject with a parent!")
			return
		self.location = newLocation
	def GetLocation(self):
		if self.parent:
			return self.parent.location
		return self.location
	def elapseTime(self, secondsElapsed, currentTime):
		pass

class Sensor(LocatedObject):
	defaultValue = None
	valueType = None
	category = None
	def __init__(self, csvfile = None, category = None, **kwargs):
		super().__init__(**kwargs)
		self.csvfile = csvfile
		self.value = self.__class__.defaultValue
		self.category = category or self.__class__.category
		self.get_db_id()
	
	def get_db_id(self):
		with dbconn.cursor() as cursor:
			cursor.execute("SELECT sensor_id FROM sensor WHERE name = %s AND location = %s", (self.name, self.GetLocation()))
			results = cursor.fetchone()
			if results is None:
				cursor.execute("INSERT INTO sensor(name, location, category) VALUES (%s, %s, %s) RETURNING sensor_id", (self.name, self.GetLocation(), self.category))
				(sensor_id, ) = cursor.fetchone()
				if sensor_id:
					self.sensor_id = sensor_id
				else:
					print("Unable to insert sensor ({}, {}) into database!".format(self.name, self.GetLocation()))
			else:
				(self.sensor_id, ) = results
				print("Sensor ({}, {}) retrieved at id {}".format(self.name, self.GetLocation(), self.sensor_id))
			dbconn.commit()

	def getValue(self):
		return self.value
	def setValue(self, newValue):
		"""Raises an exception if the new value is invalid, returns the new value otherwise."""
		if not self.validate(newValue):
			raise ValueError("setValue received value that failed validation.")
		self.value = newValue
	def validate(self, newValue):
		"""
		Returns true if the value is acceptable for the sensor,
		false if it's forbidden/out of range.
		"""
		return True
	def log(self, csvfile = None, time = None, no_sql = False):
		if not no_sql:
			self.logSQL(time = time)
		self.logAsCSV(csvfile = csvfile, time = time)
		self.after_log()
	
	def after_log(self):
		pass

	def logAsCSV(self, csvfile = None, time = None):
		if time is None:
			time = datetime.datetime.now()
		if csvfile is None:
			if self.csvfile is not None:
				csvfile = self.csvfile
			else:
				raise ValueError("LogAsCSV called with no CSV file set or provided!")
		
		csvfile.write("{},{},{},{}\n".format(self.sensor_id, time.strftime(timeFormat), self.getValue(), "production" if isProduction else "testing"))
		
	def logSQL(self, time = None):
		if time is None:
			time = datetime.datetime.now()
		if self.sensor_id is None:
			print("Attempted to logSQL with no id!")
			return
		with dbconn.cursor() as cursor:
			cursor.execute("INSERT INTO SensorEvent (sensor_id, time, value, dataset) VALUES (%s, %s, %s, %s)", (self.sensor_id, time, self.getValue(), "production" if isProduction else "testing"))
		#dbconn.commit() # moved to house.log
	
class BinarySensor(Sensor):
	defaultValue = False
	def toggle(self):
		return self.setValue(not self.getValue())
	def validate(self, newValue):
		if not super().validate(newValue):
			return False
		if not isinstance(newValue, bool):
			return False
		return True

class NumericSensor(Sensor):
	defaultValue = 0.0
	def validate(self, newValue):
		if not super().validate(newValue):
			return False
		if not isinstance(newValue, int) and not isinstance(newValue, float):
			return False
		return True
	def addValue(self, valueChange):
		return self.setValue(self.getValue() + float(valueChange))

class ActuatorDevice(LocatedObject):
	sensorType = None
	defaultState = None
	def __init__(self, sensorType = None, csvfile = None, **kwargs):
		super().__init__(**kwargs)
		self.state = self.__class__.defaultState
		sensorType = sensorType or self.__class__.sensorType
		if sensorType is not None:
			self.sensor = sensorType(name = f"{self.name} Sensor", parent = self, csvfile = csvfile)
		else:
			self.sensor = None
	
	def actuate(self, newState, time = None):
		if not self.validate(newState):
			raise ValueError("Actuator device actuated into invalid state")
		self.state = newState
		if self.sensor is not None:
			self.sensor.setValue(newState)
	
	def log(self, csvfile = None, time = None, no_sql = False):
		if not no_sql:
			self.logSQL(time=time)
		self.logAsCSV(csvfile=csvfile, time=time)
		self.after_log()
	
	def after_log(self):
		self.sensor.after_log()

	def logAsCSV(self, csvfile = None, time = None):
		if self.sensor is not None:
			return self.sensor.logAsCSV(csvfile = csvfile, time = time)
	
	def logSQL(self, time = None):
		if self.sensor is not None:
			return self.sensor.logSQL(time = time)

	def validate(self, newState):
		return True

class BinaryDevice(ActuatorDevice):
	defaultState = False
	sensorType = BinarySensor
	def toggle(self, time = None):
		self.actuate(not self.state, time = time)

class PowerUsageSensor(NumericSensor):
	category = "power"
	def __init__(self, power_usage = 0.6/3600, **kwargs):
		super().__init__(**kwargs)
		self.power_usage = power_usage
	def usePower(self, secondsElapsed):
		self.addValue(self.power_usage * secondsElapsed)
	def after_log(self):
		self.setValue(0.0) # we only log the power used between polls

class WaterUsageSensor(NumericSensor):
	category = "water"
	def __init__(self, water_usage = 0.6/3600, **kwargs):
		super().__init__(**kwargs)
		self.water_usage = water_usage
	def useWater(self, secondsElapsed):
		self.addValue(self.water_usage * secondsElapsed)
	def after_log(self):
		self.setValue(0.0) # we only log the water used between polls

class Shower(BinaryDevice):
	WATER_USAGE = 2.5/60 # 2.5 gallons per minute
	#shower duration 10mins, uses 25gal total
	def __init__(self, csvfile=None, **kwargs):
		super().__init__(csvfile = csvfile, **kwargs)
		self.water_usage_sensor = WaterUsageSensor(name = f"{self.name} Water Usage", water_usage = Shower.WATER_USAGE, parent = self, csvfile = csvfile)
	
	def elapseTime(self, secondsElapsed, currentTime):
		super().elapseTime(secondsElapsed, currentTime)
		if self.state:
			self.water_usage_sensor.useWater(secondsElapsed)
	
	def logAsCSV(self, csvfile = None, time = None):
		super().logAsCSV(csvfile = csvfile, time = time)
		self.water_usage_sensor.logAsCSV(csvfile, time)

	def logSQL(self, time = None):
		super().logSQL(time = time)
		self.water_usage_sensor.logSQL(time)
	
	def after_log(self):
		super().after_log()
		self.water_usage_sensor.after_log()

class Bathtub(BinaryDevice):
	WATER_USAGE = 3/60 # 3 gallons per minute
	#bath duration 10mins, uses 30gal total
	def __init__(self, csvfile=None, **kwargs):
		super().__init__(csvfile = csvfile, **kwargs)
		self.water_usage_sensor = WaterUsageSensor(name = f"{self.name} Water Usage", water_usage = Shower.WATER_USAGE, parent = self, csvfile = csvfile)
	
	def elapseTime(self, secondsElapsed, currentTime):
		super().elapseTime(secondsElapsed, currentTime)
		if self.state:
			self.water_usage_sensor.useWater(secondsElapsed)
	
	def logAsCSV(self, csvfile = None, time = None):
		super().logAsCSV(csvfile = csvfile, time = time)
		self.water_usage_sensor.logAsCSV(csvfile, time)

	def logSQL(self, time = None):
		super().logSQL(time = time)
		self.water_usage_sensor.logSQL(time)
	
	def after_log(self):
		super().after_log()
		self.water_usage_sensor.after_log()

class Light(BinaryDevice): # False -> Off, True -> On
	KILOWATT_SECONDS = 0.06/3600 # converting 60Wh to kilowatt-seconds
	def __init__(self, csvfile = None, **kwargs):
		super().__init__(csvfile = csvfile, **kwargs)
		self.power_usage_sensor = PowerUsageSensor(name = f"{self.name} Power Usage", power_usage = Light.KILOWATT_SECONDS, parent = self, csvfile = csvfile)
	
	def elapseTime(self, secondsElapsed, currentTime):
		super().elapseTime(secondsElapsed, currentTime)
		if(self.state):
			self.power_usage_sensor.usePower(secondsElapsed)
	
	def logAsCSV(self, csvfile = None, time = None):
		super().logAsCSV(csvfile = csvfile, time = time)
		self.power_usage_sensor.logAsCSV(csvfile, time)

	def logSQL(self, time = None):
		super().logSQL(time = time)
		self.power_usage_sensor.logSQL(time)
	
	def after_log(self):
		super().after_log()
		self.power_usage_sensor.after_log()

class Window(BinaryDevice): # False -> Closed, True -> Open
	"""TODO: add some methods for user-readable state output, i.e. return closed/open instead of bool"""
	pass

class Door(BinaryDevice): # See above for window
	pass

class Hvac(BinaryDevice):
	KILOWATT_SECONDS = 3.5/3600 # 3500Wh to kilowatt-seconds
	HEAT_PER_SECOND = 1/60 # 1F per 60 seconds of operation
	def __init__(self, defaultTarget = 70.0, csvfile = None, **kwargs):
		super().__init__(csvfile = csvfile, **kwargs)
		self.targetTemp = defaultTarget
		self.heating = False
		self.power_usage_sensor = PowerUsageSensor(name = f"{self.name} Power Usage", power_usage = Hvac.KILOWATT_SECONDS, parent = self, csvfile = csvfile)
	def setTarget(self, num):
		self.targetTemp = float(num)
	def getInternalTemperature(self):
		return self.house.getSensorByClass(InternalThermostatSensor).getValue()
	def getExternalTemperature(self):
		return self.house.getSensorByClass(ExternalThermostatSensor).getValue()
	def elapseTime(self, secondsElapsed, currentTime):
		internal_temperature = self.getInternalTemperature()
		if (internal_temperature < (self.targetTemp - 2) or internal_temperature > (self.targetTemp + 2)) and not self.state:
			self.actuate(True, time = currentTime)
			self.heating = internal_temperature < self.targetTemp
		if self.state:
			# we need to be on for at least one second
			# but can't hardcode it in case we increase the simulation timestep
			seconds_needed = max(abs(self.targetTemp - internal_temperature) / Hvac.HEAT_PER_SECOND, 1)
			seconds_taken = min(seconds_needed, secondsElapsed)
			if self.state:
				self.power_usage_sensor.usePower(seconds_taken)
			self.house.getSensorByClass(InternalThermostatSensor).addValue(Hvac.HEAT_PER_SECOND * seconds_taken)
			internal_temperature = self.getInternalTemperature()
			if self.heating and internal_temperature >= self.targetTemp:
				self.actuate(False, time = currentTime)
			if not self.heating and internal_temperature <= self.targetTemp:
				self.actuate(False, time = currentTime)
		super().elapseTime(secondsElapsed, currentTime)
	
	def logAsCSV(self, csvfile = None, time = None):
		super().logAsCSV(csvfile = csvfile, time = time)
		self.power_usage_sensor.logAsCSV(csvfile, time)
	
	def logSQL(self, time = None):
		super().logSQL(time = time)
		self.power_usage_sensor.logSQL(time)
	
	def after_log(self):
		super().after_log()
		self.power_usage_sensor.after_log()

class ThermostatSensor(NumericSensor):
	pass

class InternalThermostatSensor(ThermostatSensor):
	pass

class ExternalThermostatSensor(ThermostatSensor):
	pass

class Event():
	def __init__(self, time, callback):
		self.time = time
		self.callback = callback
		self.fired = False
		self.created_at = datetime.datetime.now()
		self.fired_at = None
	def getTimestamp(self):
		return self.time.timestamp()
	def invoke(self):
		if not self.fired:
			self.callback()
			self.fired = True
			self.fired_at = datetime.datetime.now()
	def __lt__(self, other):
		return self.time < other.time
	def __repr__(self):
		return f"[{self.time}; CREATED: {self.created_at}; {('FIRED: ' + str(self.fired_at)) if self.fired else 'Not fired'};]"
