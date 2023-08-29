"""Driver for CCS811 sensors (eCO₂ and eTVOC):
    Adresse i2c: 0x5A or 0x5B depending on status of ADDR pin
    Official website of the manufacturer: www.sciosense.com
"""

import time
from ccs811 import CCS811


class CCS811Bootloader(CCS811):
    """Implementation of the Bootloader Register Overview"""

    def _get_app_is_erase(self):
        """False: No erase completed.
        True: Application erase operation completed successfully."""
        return self._get_status(0b01000000)

    def _get_app_is_verified(self):
        """False: No verify completed.
        True: Application verify operation completed successfully."""
        return self._get_status(0b00100000)

    def _app_erase(self):
        """the device will start the application erase."""
        self.i2c.writeto_mem(self.addr, 0xF1, bytes([0xE7, 0xA7, 0xE6, 0x09]))
        # the application software must wait 500ms before issuing any transactions.
        time.sleep_ms(500)

    def _app_verify(self):
        """Starts the process of the bootloader checking though the application to make
        sure a full image is valid."""
        self.i2c.writeto(self.addr, bytes([0xF3]))
        # The application software must wait 70ms before issuing any transactions.
        time.sleep_ms(70)

    def _app_start(self):
        """Application start."""
        self.i2c.writeto(self.addr, bytes([0xF4]))
        # Time between giving the APP_START command in boot mode and the device being ready.
        time.sleep_ms(1)

    def upgrade_fw(self, file_path):
        """Reprogramming the CCS811 device with a new Application code binary file.
        True: successful upgrade.
        False: program code invalid."""
        if self._get_is_ready_to_measure():
            self._sw_reset()

        self._app_erase()
        while not self._get_app_is_erase():
            time.sleep_ms(100)

        with open(file_path, "rb") as file:
            data = file.read(8)
            while data:
                self.i2c.writeto_mem(self.addr, 0xF2, data)
                data = file.read(8)

        self._app_verify()
        while not self._get_app_is_verified():
            time.sleep_ms(100)

        return self._get_app_is_valid()
