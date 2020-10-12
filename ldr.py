import spidev
import time
import os


class LDR():
    def __init__(self):
        # Define sensor channels
        self.light_channel = 0
        self.spi = self.open_SPI_bus()

    def open_SPI_bus(self):
        spi = spidev.SpiDev()
        spi.open(0, 0)
        spi.max_speed_hz = 1000000
        return spi

    def ReadChannel(self):
        ''' # Function to read SPI data from MCP3008 chip. Channel must be an integer 0-7 '''

        adc = self.spi.xfer2([1, (8+self.light_channel) << 4, 0])
        data = ((adc[1] & 3) << 8) + adc[2]
        return data

    def ConvertVolts(self, data, places):
        '''Function to convert data to voltage level, rounded to specified number of decimal places'''
        volts = (data * 3.3) / float(1023)
        volts = round(volts, places)
        return volts
