"""Driver for CCS811 sensors (eCO₂ and eTVOC):
    Adresse i2c: 0x5A or 0x5B depending on status of ADDR pin
    Official website of the manufacturer: www.sciosense.com
"""

import time
from ccs811 import CCS811
from ccs811bootloader import CCS811Bootloader


class CCS811Application(CCS811):
    """Implementation of the Application Register Overview."""

    def __init__(self, i2c, addr):
        """Parameters:
        i2c: instance of machine.I2C
        addr: i2c address of sensor (0x5A or 0x5B)
        mode: measurement and conditions mode"""
        super().__init__(i2c, addr)
        self.humidity = None
        self.temperature = None

        self._time_baseline = time.ticks_ms()
        self._values = {"current": None, "voltage": None}
        self._reload = {"current": True, "voltage": True}

        CCS811Bootloader(i2c, addr)._app_start()

    def _set_meas_mode(self, mode, with_int=False, with_thresh=False):
        """This is Single byte register, which is used to enable sensor drive
        mode and interrupts."""
        register = bytes([mode << 4 | with_int << 3 | with_thresh << 2])
        self.i2c.writeto_mem(self.addr, 0x01, register)

    def _set_env_data(self, humidity, temperature):
        """Temperature and humidity data can be written to enable compensation."""
        register = bytearray(4)
        humidity = (int(humidity) << 1) | int((humidity % 1) * 512)
        temperature = (int(temperature + 25) << 1) | int((temperature % 1) * 512)
        register[0] = humidity >> 8
        register[1] = humidity & 0xFF
        register[2] = temperature >> 8
        register[3] = temperature & 0xFF
        self.i2c.writeto_mem(self.addr, 0x05, register)

    @property
    def baseline(self):
        """The encoded current baseline value can be read."""
        if time.ticks_diff(time.ticks_ms(), self._time_baseline) < 72000:
            print(
                """Warning: After configuration of the sensor in mode 1-4,
                  wait 20m before accurate readings are generated."""
            )
        baseline = self.i2c.readfrom_mem(self.addr, 0x11, 2)
        return (baseline[0] << 8) | baseline[1]

    @baseline.setter
    def baseline(self, baseline):
        """Apreviously saved encoded baseline can be written."""
        register = bytearray(2)
        register[0] = baseline >> 8
        register[1] = baseline & 0xFF
        self.i2c.writeto_mem(self.addr, 0x11, register)
