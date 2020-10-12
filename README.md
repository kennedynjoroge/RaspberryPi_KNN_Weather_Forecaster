# Raspberry Pi Weather Predictor
## Components
- Raspberry Pi 4
- Breadboard
- Bme280 humidity, temperature and air pressure Sensor
- LDR light intensity sensor
- 10k resistor
- MCP 3008 Analogue to Digital Converter.
- Lots of jumper cables.

## Steps
1. Read ambient temperature, barometer, humidity, light internsity
2. Make weather forecast based on rules i.e if, else 
3. Use the rules data to to train KNN model on python notebook
4. Export the model from notebook and import it into raspberry pi
4. Read raw values and pass to KNN model for weather prediction.

## References
MCP3008 - https://www.raspberrypi-spy.co.uk/2013/10/analogue-sensors-on-the-raspberry-pi-using-an-mcp3008/
BME - https://www.raspberrypi-spy.co.uk/2016/07/using-bme280-i2c-temperature-pressure-sensor-in-python/

## License
Distributed under the MIT License.
