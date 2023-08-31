"""Driver for CCS811 sensors (eCO₂ and eTVOC):
    Adresse i2c: 0x5A or 0x5B depending on status of ADDR pin
    Official website of the manufacturer: www.sciosense.com
"""

import time
from micropython import const

__author__ = "Jonathan Fromentin"
__credits__ = ["Jonathan Fromentin"]
__license__ = "CeCILL version 2.1"
__version__ = "1.0.0"
__maintainer__ = "Jonathan Fromentin"

# import network
# ap = network.WLAN(network.AP_IF)
# ap.active(False)

CCS_I2C_ADDR = const(0x5A)  # Default I2C address
CCS_I2C_ALT_ADDR = const(0x5B)  # Alternate I2C address
CCS_LM_TH = const(0x05DC)  # Low to Medium Threshold default (1500ppm)
CCS_MH_TH = const(0x09C4)  # Medium to High Threshold default (2500ppm)

CCS_MODE_0 = const(0x0)  # Idle (Measurements are disabled in this mode)
CCS_MODE_1 = const(0x1)  # Constant power mode, IAQ measurement every second
CCS_MODE_2 = const(0x2)  # Pulse heating mode IAQ measurement every 10s
CCS_MODE_3 = const(0x3)  # Low power pulse heating mode IAQ measurement every 60s
CCS_MODE_4 = const(0x4)  # Constant power mode, sensor measurement every 250ms


class CCS811:
    """Class based on CCS811 documentation (v3)."""

    def __init__(self, i2c, addr):
        """Parameters:
        i2c: instance of machine.I2C
        addr: i2c address of sensor (default: 0x5A and alternative: 0x5B)"""
        # Time between power on and the device being ready for new I²C commands
        time.sleep_ms(20)

        self.i2c = i2c
        self.addr = addr

        # Check if sensor is vailable at i2c bus address
        if self.addr not in self.i2c.scan():
            raise ValueError("CCS811 not found")

        # Check HW_ID register (0x20) - correct value 0x81
        if self.hw_id != 0x81:
            raise ValueError("Wrong Hardware ID")

        if not self._get_app_is_valid():
            raise ValueError("Application not valid.")

    def _get_is_ready_to_measure(self):
        """False: Firmware is in boot mode, this allows new firmware to be loaded.
        True: Firmware is in application mode. CCS811 is ready to take ADC measurements.
        """
        return self._get_status(0b10000000)

    def _get_app_is_valid(self):
        """False: No application firmware loaded.
        True: Valid application firmware loaded."""
        return self._get_status(0b00010000)

    def _get_data_is_ready(self):
        """False: No new data samples are ready.
        True: A new data sample is ready."""
        return self._get_status(0b00001000)

    def _get_status(self, bit):
        """Return the boolean value for the bit of status."""
        status = self.i2c.readfrom_mem(self.addr, 0x00, 1)[0]
        if status & 0b00000001:
            self._error_id()
        return bool(status & bit)

    @property
    def hw_id(self):
        """Hardware ID. The value is 0x81."""
        return self.i2c.readfrom_mem(self.addr, 0x20, 1)[0]

    @property
    def hw_version(self):
        """Hardware Version. The value is 0x1X."""
        return self.i2c.readfrom_mem(self.addr, 0x21, 1)[0]

    @property
    def fw_boot_version(self):
        """Firmware Boot Version."""
        return self._fw_version(0x23)

    @property
    def fw_app_version(self):
        """Firmware Application Version."""
        return self._fw_version(0x24)

    def _fw_version(self, addr_register):
        """Return the Firmware Boot Version or the Firmware Application Version."""
        fwv = self.i2c.readfrom_mem(self.addr, addr_register, 2)
        # Format fo result:  major.minor.trivial
        return "{}.{}.{}".format(fwv[0] >> 4, fwv[0] & 0xF, fwv[1])

    def _error_id(self):
        """Raise an exception if an error is identified."""
        dict_err = {
            0: "WRITE_REG_INVALID",
            1: "READ_REG_INVALID",
            2: "MEASMODE_INVALID",
            3: "MAX_RESISTANCE",
            4: "HEATER_FAULT",
            5: "HEATER_SUPPLY",
        }

        error_code = self.i2c.readfrom_mem(self.addr, 0xE0, 1)[0]
        if error_code in dict_err:
            raise ValueError(dict_err[error_code])

    def _sw_reset(self):
        """the device will reset and return to BOOT mode."""
        self.i2c.writeto_mem(self.addr, 0xFF, bytes([0x11, 0xE5, 0x72, 0x8A]))
        # Time after giving the SW_RESET command and the device being ready for new I²C commands
        time.sleep_ms(2)
