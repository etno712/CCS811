"""Driver for CCS811 sensors (eCO₂ and eTVOC):
    Adresse i2c: 0x5A or 0x5B depending on status of ADDR pin
    Official website of the manufacturer: www.sciosense.com
"""

from ccs811 import CCS_MODE_4
from ccs811application import CCS811Application


class CCS811Raw(CCS811Application):
    """Implementation of the Application Register Overview for modes 4.
    Constant power mode, sensor measurement every 250ms,
    only raw data is updated"""

    def __init__(self, i2c, addr):
        """Parameters:
        i2c: instance of machine.I2C
        addr: i2c address of sensor"""
        super().__init__(i2c, addr)

        self._set_meas_mode(CCS_MODE_4)

    @property
    def data_is_ready(self):
        """Return True, if new raw data is ready."""
        return self._get_data_is_ready()

    @property
    def current(self):
        """Raw data current"""
        if self._reload["current"]:
            self._values["voltage"], self._values["current"] = self._get_raw_data()
            self._values["voltage"] = False
        else:
            self._reload["current"] = True

        return self._values["current"]

    @property
    def voltage(self):
        """Raw data voltage"""
        if self._reload["voltage"]:
            self._values["voltage"], self._values["current"] = self._get_raw_data()
            self._values["current"] = False
        else:
            self._reload["voltage"] = True

        return self._values["voltage"]

    def _get_raw_data(self):
        """Raw ADC data values for resistance and current source used."""
        if (self.humidity is None) != (self.temperature is None):
            print("Warning: Environment data is incomplete")
        if self.humidity and self.temperature:
            self._set_env_data(self.humidity, self.temperature)

        raw_data = self.i2c.readfrom_mem(self.addr, 0x03, 2)
        current = raw_data[0] >> 2
        voltage = (1.65 / 1023) * (((raw_data[0] & 0x3) << 8) | raw_data[1])
        return (voltage, current)
