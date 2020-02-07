#!/usr/bin/python3

from flask import Flask
from config import Config
from flask_ask import Ask, statement, question
from flask_redis import FlaskRedis
import requests
import json
import atexit
from apscheduler.scheduler import Scheduler
from sensors import MCP3008, DS18B20, DHT11
import zmq
import datetime

redis_client = FlaskRedis()

def get_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    redis_client.init_app(app)
    ask = Ask(app, '/alexa')
    return app

app = create_app()

# Initiates ZMQ client so that we can talk to the server
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect(app.config['REQ_SOCKET'])

# Initiates APScheduler to make hourly API calls to weather service
cron = Scheduler(daemon=True)
cron.start()

# Uses IP address to geolocate city and country for weather service
# If normal (200 code), returns {city}, {country}
# If not normal, returns an error with the status code
def geolocate_me():
    response = requests.get('http://ipinfo.io/json')
    if response.status_code == '200':
        data = json.load(response)
        return '{}, {}'.format(data['city'], data['country'])
    else:
        raise ValueError('Geolocation Error: {}'.format(response.status_code))

# Uses geolocation data to query weather data once an hour
# If normal (200 code), saves weather data in Redis database with a 1-hour time limit
# If not normal, returns an error with the status code
@cron.interval_schedule(hours=1)
def get_weather_data():
    location = geolocate_me()
    access_key = app.config['WEATHER_ACCESS_KEY']
    url = 'https://api.weatherstack.com/current?' + access_key + '&' + location
    response = requests.get(url)
    if response.status_code == '200':
        data = json.load(response)
        redis_client.set('weather', data, ex=3600)
    else:
        raise ValueError('Weather API Error: {}'.format(response.status_code))

# If normal (entry exists), returns weather data from Redis database
# If not normal, returns an error
@app.route('/weather')
def send_weather_data():
    if redis_client.exists('weather') == '1':
        return redis_client.get('weather')
    else:
        raise ValueError('Redis Database Error: No entry!')

# Returns sensor data
@app.route('/sensor/<sensor>')
def send_sensor_data(sensor):
    sensor = sensor.lower()
    if sensor == 'temperature':
        temperature = DS18B20()
        sensor_data = temperature.read_temperature()
    elif sensor == 'humidity':
        humidity = DHT11()
        sensor_data = humidity 
    elif sensor == 'light':
        light = MCP3008()
        sensor_data = light.read(channel=0)
    return sensor_data

# Placeholder function to symbolize querying how cold the AC is blowing without dealing with LIRC
def get_current_temperature():
    return int(20)

# Placeholder function to symbolize turning the AC up by {degrees} without actually dealing with LIRC
def warmer_climate_control(degrees):
    if type(degrees) == 'int':
        temperature = get_current_temperature()
        return temperature + degrees
    else:
        raise ValueError('Expected integer!')

# Placeholder function to symbolize turning the AC down by {degrees} without actually dealing with LIRC
def cooler_climate_control(degrees):
    if type(degrees) == 'int':
        temperature = get_current_temperature()
        return temperature - degrees
    else:
        raise ValueError('Expected integer!')

# Alexa: "Hey Alexa, start Iffy-Weather!"
@ask.launch
def start_skill():
    return question('How can I help?')

# Alexa: "Turn the AC up 5 degrees"
# Increases the temperature and sends an update to the server via ZMQ
# Timestamp is in UTC for time zone standardization
@ask.intent('TemperatureUp')
def temperature_up(degrees):
    warmer_climate_control(degrees)
    server_update_message = '+{} @ {}'.format(degrees, datetime.datetime.utcnow())
    socket.send(str.encode(server_update_message))
    return statement('Increased the temperature by {} degrees.'.format(degrees))

# Alexa: "Turn the AC down by 5 degrees"
# Decreases the temperature and sends an update to the server via ZMQ
# Timestamp is in UTC for time zone standardization
@ask.intent('TemperatureDown')
def temperature_down(degrees):
    cooler_climate_control(degrees)
    server_update_message = '-{} @ {}'.format(degrees, datetime.datetime.utcnow())
    socket.send(str.encode(server_update_message))
    return statement('Decreased the temperature by {} degrees.'.format(degrees))

# Allows server to increase AC temperature, but only if an integer is provided
@app.route('/increase-temperature/<degrees>')
def increase_temperature(degrees):
    if type(degrees) == 'int':
        warmer_climate_control(degrees)
    else:
        raise ValueError('Expected integer!')

# Allows server to decrease AC temperature, but only if an integer is provided
@app.route('/decrease-temperature/<degrees>')
def decrease_temperature(degrees):
    if type(degrees) == 'int':
        cooler_climate_control(degrees)
    else:
        raise ValueError('Expected integer!')

# If web service stops, weather queries also shut down
atexit.register(lambda: cron.shutdown(wait=False))

if __name__ == '__main__':
    app.run(host='0.0.0.0')