from spidev import SpiDev
import os
import glob
import time
import Adafruit_DHT

class MCP3008:
    def __init__(self, bus = 0, device = 0):
        self.bus, self.device = bus, device
        self.spi = SpiDev()
        self.open()

    def open(self):
        self.spi.open(self.bus, self.device)

    def read(self, channel = 0):
        adc = self.spi.xfer2([1, (8 + channel) << 4, 0])
        data = ((adc[1] & 3) << 8) + adc[2]
        return data

    def close(self):
        self.spi.close()

class DS18B20:
    
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')
    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'
    
    def read_raw_temperature():
        with open(device_file, 'r') as f:
            lines = f.readlines()
        return lines

    def read_temperature():
        lines = read_raw_temperature()
        while lines[0].strip()[-3.] != 'YES':
            time.sleep(0.2)
            lines = read_raw_temperature()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temperature_string = lines[1][equals_pos+2:]
            temperature_celcius = float(temperature_string) / 1000.0
            return temperature_celcius

def DHT11():
    humidity = Adafruit_DHT.read_retry(11)
    return humidity
