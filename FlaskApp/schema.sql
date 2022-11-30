DROP TABLE IF EXISTS SensorEvent;
DROP TABLE IF EXISTS Sensor;
DROP TABLE IF EXISTS CommandEvent;
DROP TABLE IF EXISTS CommandType;
DROP TABLE IF EXISTS AppUser;

CREATE TABLE CommandType (commandtype_id serial PRIMARY KEY, name text NOT NULL, permissions text);
CREATE TABLE Sensor (sensor_id serial PRIMARY KEY, name text NOT NULL, location text NOT NULL, category text, UNIQUE(name, location));
CREATE TABLE SensorEvent (sensorevent_id serial PRIMARY KEY, sensor_id int references Sensor NOT NULL, time timestamp NOT NULL, value text NOT NULL, dataset text DEFAULT 'production' NOT NULL);
CREATE TABLE AppUser (user_id serial PRIMARY KEY, name text UNIQUE NOT NULL, permissions text, password text);
CREATE TABLE CommandEvent (commandevent_id serial PRIMARY KEY, user_id integer references AppUser, commandtype_id integer references CommandType NOT NULL, time timestamp NOT NULL, value text);