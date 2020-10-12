from bme280 import BME280  # Detect temperature, humidity and air pressure
from ldr import LDR  # Detect light intensity from photoresistor
from time import sleep, strftime
from csv import DictWriter
import pickle
import numpy as np

# Read from sensors and store values in a dictionary
# Constants & Variables
date_format = "{:Y%m%d_%H%M%S}"
BME_I2C_ADDRESS = 0x77  # Default device I2C address
delay = 5
weather = {}

# Import Model
filename = 'weather_knn_model.sav'
weather_knn_model = pickle.load(open(filename, 'rb'))

# Instantiate weather classes
tmp_hum_pre_sensor = BME280(BME_I2C_ADDRESS)
light_sensor = LDR()

# Read weather values and assign them to a dictionary
with open('/home/pi/Projects/Weather-Station/knn_weather_database.csv', 'a') as weather_log:
    headers = ['temperature_raw', 'pressure_raw', 'humidity_raw', 'sky_raw', 'weather_time',
               'weather', 'forecast']
    writer = DictWriter(weather_log, fieldnames=headers)
    # writer.writeheader()
    while True:
        # Temp in celsius
        # Air pressure in hectopascal hPa
        # Light is in Lux http://lednique.com/opto-isolators-2/light-dependent-resistor-ldr/
        weather = tmp_hum_pre_sensor.read_BME280_sensors()
        weather['sky_raw'] = light_sensor.ReadChannel()  # read raw values
        print("Input>> ", weather)
        writer.writerow(weather)
        raw_weather_feed = np.array(tuple(weather.values())).reshape(1, -1)
        weather_state = weather_knn_model.predict(
            raw_weather_feed)  # Prediction
        weather_state = str(weather_state.tolist()).strip('[').strip(']')
        print(weather_state)
        weather['weather_time'] = strftime("%Y-%m-%d %H:%M:%S")
        weather['weather'] = weather_state
        print("Output>> ", weather)
        writer.writerow(weather)
        sleep(delay)
