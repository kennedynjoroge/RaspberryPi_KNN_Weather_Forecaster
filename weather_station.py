from bme280 import BME280  # Detect temperature, humidity and air pressure
from ldr import LDR  # Detect light intensity from photoresistor
from time import sleep, strftime
from csv import DictWriter


def bin_raw_measures(weather):
    '''
    Input: Dictionary with temperature, pressure, humidity and light intensity
    Output: Binned measures of temperature, pressure, humidity and light
    '''
    # Temp Hot or cold? <=15 degrees cold else Hot : https://www.gmp-compliance.org/gmp-news/what-are-the-regulatory-definitions-for-ambient-room-temperature-and-cold-chain
    if weather['temperature_raw'] > 15:
        weather['temperature'] = 'high'
    else:
        weather['temperature'] = 'low'

    # Compare with readings in Mombasa https://www.startribune.com/fixit-what-is-the-ideal-winter-indoor-humidity-level/11468916/
    if weather['pressure_raw'] > 845:
        weather['pressure'] = 'high'
    else:
        weather['pressure'] = 'low'

    # Humidity scale: https://www.startribune.com/fixit-what-is-the-ideal-winter-indoor-humidity-level/11468916/
    if weather['humidity_raw'] > 55:
        weather['humidity'] = 'wet'
    else:
        weather['humidity'] = 'dry'

    # Light http://lednique.com/opto-isolators-2/light-dependent-resistor-ldr/
    if weather['sky_raw'] > 700:
        weather['sky'] = 'overcast'
    else:
        weather['sky'] = 'sunny'

    return weather


def get_weather_forecast_state(weather):
    '''
    Input: Dictionary with binned measures of temperature, pressure, humidity and light intensity
    Output: Weather and forecast
    '''
    # Weather rules
    if weather['temperature'] == 'high' and weather['humidity'] == 'dry' and weather['sky'] == 'sunny':
        weather['weather'] = 'good'
    elif weather['humidity'] == 'wet':
        weather['weather'] = 'bad'
    elif weather['temperature'] == 'low':
        weather['weather'] = 'bad'
    elif weather['temperature'] == 'low':
        weather['weather'] = 'bad'
    elif weather['sky'] == 'overcast':
        weather['weather'] = 'bad'
    else:
        weather['weather'] = 'uncertain'

    # Forecast rules. NB: Pressure = barometer
    if weather['pressure'] == 'high':
        weather['forecast'] = 'good'
    elif weather['pressure'] == 'low':
        weather['forecast'] = 'bad'
    else:
        weather['forecast'] = 'uncertain'
    return weather


# Read from sensors and store values in a dictionary
# Constants & Variables
date_format = "{:Y%m%d_%H%M%S}"
BME_I2C_ADDRESS = 0x77  # Default device I2C address
delay = 5
weather = {}

# Instantiate weather classes
tmp_hum_pre_sensor = BME280(BME_I2C_ADDRESS)
light_sensor = LDR()
# Read weather values and assign them to a dictionary
with open('/home/pi/Projects/Weather-Station/weather_database.csv', 'a') as weather_log:
    headers = ['temperature_raw', 'pressure_raw', 'humidity_raw', 'sky_raw', 'weather_time',
               'temperature', 'pressure', 'humidity', 'sky', 'weather', 'forecast']
    writer = DictWriter(weather_log, fieldnames=headers)
    # writer.writeheader()
    while True:
        # Temp in celsius
        # Air pressure in hectopascal hPa
        # Light is in Lux http://lednique.com/opto-isolators-2/light-dependent-resistor-ldr/
        weather = tmp_hum_pre_sensor.read_BME280_sensors()
        weather['weather_time'] = strftime("%Y-%m-%d %H:%M:%S")
        print(weather)
        weather['sky_raw'] = light_sensor.ReadChannel()  # read raw values
        weather = bin_raw_measures(weather)  # Convert raw values to bins
        weather = get_weather_forecast_state(
            weather)  # Get weather and forecast
        # weather_log.write(str(weather))
        # weather_log.write("test")

        writer.writerow(weather)
        print(weather)

        sleep(delay)
