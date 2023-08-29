"""Driver for CCS811 sensors (eCO₂ and eTVOC):
    Adresse i2c: 0x5A or 0x5B depending on status of ADDR pin
    Official website of the manufacturer: www.sciosense.com
"""

from ccs811 import CCS_I2C_ADDR, CCS_MODE_0, CCS_MODE_1, CCS_MODE_4
from ccs811bootloader import CCS811Bootloader
from ccs811raw import CCS811Raw
from ccs811algoresult import CCS811AlgoResult


class CCS811Factory:
    """Factory class for managing CCS811 modes."""

    def __new__(
        cls, i2c, addr=CCS_I2C_ADDR, mode=CCS_MODE_1, with_int=False, with_thresh=False
    ):
        if mode == CCS_MODE_0:
            return CCS811Bootloader(i2c, addr)
        if mode == CCS_MODE_4:
            return CCS811Raw(i2c, addr)
        return CCS811AlgoResult(i2c, addr, mode, with_int, with_thresh)
