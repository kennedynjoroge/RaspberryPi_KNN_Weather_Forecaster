'''
Objective: Detect temperature, humidity and airpressure of ambient environment
Sensor used : https://www.tinyosshop.com/index.php?route=product/product&filter_name=Bme280&filter_description=true&filter_sub_category=true&product_id=952
Datasheet: https://www.tinyosshop.com/datasheet/BST-BME280_DS001-10.pdf
Temp: Operational : -40 to 85 degrees. Full accuracy : 0 to 65 degrees celsius
Pressure : 300 to 1100
This temperature value depends on the Printed circuit board temperature, sensor element self-heating and ambient temperature and is typically
above ambient temperature.
'''
import smbus
import time
from ctypes import c_short
from ctypes import c_byte
from ctypes import c_ubyte


class BME280:
    def __init__(self, i2c_address):
        self.DEVICE = i2c_address  # Device's I2C address
        self.bus = smbus.SMBus(1)

    def get_short(self, data, index):
        ''' return two bytes from data as a signed 16-bit value  '''
        return c_short((data[index+1] << 8) + data[index]).value

    def get_unsigned_short(self, data, index):
        ''' return two bytes from data as an unsigned 16-bit value '''
        return (data[index+1] << 8) + data[index]

    def get_char(self, data, index):
        ''' return one byte from data as a signed char '''
        result = data[index]
        if result > 127:
            result -= 256
        return result

    def get_unsigned_char(self, data, index):
        ''' return one byte from data as an unsigned char '''
        result = data[index] & 0xFF
        return result

    def read_BME280_sensors(self):
        ''' Read sensor values. Refer to datasheet(URL provided at top) for more details regarding 
        the addresses and logic used to read the measures '''

        # Register Addresses - page 25
        addr = self.DEVICE
        REG_DATA = 0xF7
        REG_CONTROL = 0xF4
        REG_CONTROL_HUM = 0xF2

        # Oversample setting - page 27
        OVERSAMPLE_TEMP = 2
        OVERSAMPLE_PRES = 2
        MODE = 1

        # Oversample setting for humidity register - page 26
        OVERSAMPLE_HUM = 2
        self.bus.write_byte_data(addr, REG_CONTROL_HUM, OVERSAMPLE_HUM)

        control = OVERSAMPLE_TEMP << 5 | OVERSAMPLE_PRES << 2 | MODE
        self.bus.write_byte_data(addr, REG_CONTROL, control)

        # Read blocks of calibration data from EEPROM
        # See Page 22 data sheet
        cal1 = self.bus.read_i2c_block_data(addr, 0x88, 24)
        cal2 = self.bus.read_i2c_block_data(addr, 0xA1, 1)
        cal3 = self.bus.read_i2c_block_data(addr, 0xE1, 7)

        # Convert byte data to word values
        dig_T1 = self.get_unsigned_short(cal1, 0)
        dig_T2 = self.get_short(cal1, 2)
        dig_T3 = self.get_short(cal1, 4)

        dig_P1 = self.get_unsigned_short(cal1, 6)
        dig_P2 = self.get_short(cal1, 8)
        dig_P3 = self.get_short(cal1, 10)
        dig_P4 = self.get_short(cal1, 12)
        dig_P5 = self.get_short(cal1, 14)
        dig_P6 = self.get_short(cal1, 16)
        dig_P7 = self.get_short(cal1, 18)
        dig_P8 = self.get_short(cal1, 20)
        dig_P9 = self.get_short(cal1, 22)

        dig_H1 = self.get_unsigned_char(cal2, 0)
        dig_H2 = self.get_short(cal3, 0)
        dig_H3 = self.get_unsigned_char(cal3, 2)

        dig_H4 = self.get_char(cal3, 3)
        dig_H4 = (dig_H4 << 24) >> 20
        dig_H4 = dig_H4 | (self.get_char(cal3, 4) & 0x0F)

        dig_H5 = self.get_char(cal3, 5)
        dig_H5 = (dig_H5 << 24) >> 20
        dig_H5 = dig_H5 | (self.get_unsigned_char(cal3, 4) >> 4 & 0x0F)

        dig_H6 = self.get_char(cal3, 6)

        # Wait in ms (Datasheet Appendix B: Measurement time and current calculation) - Page 51
        wait_time = 1.25 + (2.3 * OVERSAMPLE_TEMP) + ((2.3 *
                                                       OVERSAMPLE_PRES) + 0.575) + ((2.3 * OVERSAMPLE_HUM)+0.575)
        time.sleep(wait_time/1000)  # Wait the required time

        # Read temperature/pressure/humidity
        data = self.bus.read_i2c_block_data(addr, REG_DATA, 8)
        pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        hum_raw = (data[6] << 8) | data[7]

        # Refine temperature
        var1 = ((((temp_raw >> 3)-(dig_T1 << 1)))*(dig_T2)) >> 11
        var2 = (((((temp_raw >> 4) - (dig_T1)) *
                  ((temp_raw >> 4) - (dig_T1))) >> 12) * (dig_T3)) >> 14
        t_fine = var1+var2
        temperature = float(((t_fine * 5) + 128) >> 8)

        # Refine pressure and adjust for temperature
        var1 = t_fine / 2.0 - 64000.0
        var2 = var1 * var1 * dig_P6 / 32768.0
        var2 = var2 + var1 * dig_P5 * 2.0
        var2 = var2 / 4.0 + dig_P4 * 65536.0
        var1 = (dig_P3 * var1 * var1 / 524288.0 + dig_P2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * dig_P1
        if var1 == 0:
            pressure = 0
        else:
            pressure = 1048576.0 - pres_raw
            pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
            var1 = dig_P9 * pressure * pressure / 2147483648.0
            var2 = pressure * dig_P8 / 32768.0
            pressure = pressure + (var1 + var2 + dig_P7) / 16.0

        # Refine humidity
        humidity = t_fine - 76800.0
        humidity = (hum_raw - (dig_H4 * 64.0 + dig_H5 / 16384.0 * humidity)) * (dig_H2 / 65536.0 *
                                                                                (1.0 + dig_H6 / 67108864.0 * humidity * (1.0 + dig_H3 / 67108864.0 * humidity)))
        humidity = humidity * (1.0 - dig_H1 * humidity / 524288.0)

        if humidity > 100:
            humidity = 100
        elif humidity < 0:
            humidity = 0
        weather_readings = {}
        weather_readings['temperature_raw'] = temperature/100.0
        weather_readings['pressure_raw'] = round(pressure/100.0, 2)
        weather_readings['humidity_raw'] = round(humidity, 2)
        return weather_readings
        # return temperature/100.0, pressure/100.0, humidity
