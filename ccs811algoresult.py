"""Driver for CCS811 sensors (eCO₂ and eTVOC):
    Adresse i2c: 0x5A or 0x5B depending on status of ADDR pin
    Official website of the manufacturer: www.sciosense.com
"""

from ccs811 import CCS_LM_TH, CCS_MH_TH
from ccs811application import CCS811Application


class CCS811AlgoResult(CCS811Application):
    """Implementation of the Application Register Overview for modes 1, 2 and 3"""

    def __init__(self, i2c, addr, mode, with_int, with_thresh):
        """Parameters:
        i2c: instance of machine.I2C
        addr: i2c address of sensor (default: 0x5A and alternative: 0x5B)
        mode: measurement and conditions mode
        with_int (bool): The nINT signal is asserted (driven low) when a new
                         sample is ready.
        with_thresh (bool): if interrupt mode is enabled, only asserts the nINT
                            signal if the new data crosses one of the thresholds"""
        super().__init__(i2c, addr)

        self._values |= {"is_ready": None, "eCO2": None, "eTVOC": None}
        self._reload |= {"is_ready": True, "eCO2": True, "eTVOC": True}

        self._set_meas_mode(mode, with_int, with_thresh)

        # It is impossible to read the thresholds from the CCS811.
        # Therefore, we overwrite the values with the default value.
        self._lm_th = CCS_LM_TH
        self._mh_th = CCS_MH_TH
        self._set_thresholds(self._lm_th, self._mh_th)

    @property
    def eco2(self):
        """equivalent CO2"""
        return self._get_value("eCO2")

    @property
    def etvoc(self):
        """Equivalent total VOC"""
        return self._get_value("eTVOC")

    @property
    def current(self):
        """Raw data current"""
        return self._get_value("current")

    @property
    def voltage(self):
        """Raw data voltage"""
        return self._get_value("voltage")

    def _get_value(self, data_id):
        """Parameters:
        data_id (str): data id of _values and _reload dicts"""
        if self._reload[data_id]:
            self._get_alg_result_data()
        self._reload[data_id] = True

        return self._values[data_id]

    def _get_alg_result_data(self):
        """Update eCO2, eTVOC, status, raw data
        and raise exception if an error is detected"""
        if (self.humidity is None) != (self.temperature is None):
            print("Warning: Environment data is incomplete")
        if self.humidity and self.temperature:
            self._set_env_data(self.humidity, self.temperature)

        data = self.i2c.readfrom_mem(self.addr, 0x02, 8)
        self._values["eCO2"] = (data[0] << 8) | data[1]
        self._reload["eCO2"] = False
        self._values["eTVOC"] = (data[2] << 8) | data[3]
        self._reload["eTVOC"] = False
        self._values["is_ready"] = bool(data[4])
        self._reload["is_ready"] = False
        if data[5]:
            self._error_id()
        self._values["current"] = data[6] >> 2
        self._reload["current"] = False
        self._values["voltage"] = (1.65 / 1023) * (((data[6] & 0b11) << 8) | data[7])
        self._reload["voltage"] = False

    @property
    def data_is_ready(self):
        """Return True, if new raw data is ready."""
        if self._reload["is_ready"]:
            self._values["is_ready"] = self._get_data_is_ready()
        else:
            self._reload["is_ready"] = True
        return self._values["is_ready"]

    @property
    def low_threshold(self):
        """Thresholds for operation when interrupts are only generated when eCO2 ppm
        crosses a threshold."""
        return self._lm_th

    @low_threshold.setter
    def low_threshold(self, lm_th):
        """Thresholds for operation when interrupts are only generated when eCO2 ppm
        crosses a threshold."""
        self._lm_th = lm_th
        self._set_thresholds(self._lm_th, self._mh_th)

    @property
    def high_threshold(self):
        """Thresholds for operation when interrupts are only generated when eCO2 ppm
        crosses a threshold."""
        return self._mh_th

    @high_threshold.setter
    def high_threshold(self, mh_th):
        """Thresholds for operation when interrupts are only generated when eCO2 ppm
        crosses a threshold."""
        self._mh_th = mh_th
        self._set_thresholds(self._lm_th, self._mh_th)

    def _set_thresholds(self, lm_th, mh_th):
        """Thresholds for operation when interrupts are only generated when eCO2 ppm
        crosses a threshold."""
        register = bytearray(4)
        register[0] = lm_th >> 8
        register[1] = lm_th & 0xFF
        register[2] = mh_th >> 8
        register[3] = mh_th & 0xFF
        self.i2c.writeto_mem(self.addr, 0x10, register)
