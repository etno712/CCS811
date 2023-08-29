[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Introduction
============

Driver in MicroPython for CC811: Ultra-Low Power Digital Gas Sensor for
Monitoring Indoor Air Quality
The driver covers 100% of the sensor's application register:
* Get status register and raise ValueError when the status register reports an error.
* Give measurement mode and conditions register.
* Get ppm estimate of the equivalent CO₂ (eCO₂) level and ppb estimate of the
total VOC (eTVOC) level.
* Get raw ADC data values for resistance with voltage (V) and current (μA) source used.
* Give temperature and humidity data to enable compensation.
* Give Thresholds for operation when interrupts are only generated when eCO₂ ppm
crosses a threshold.
* Get/Give the baseline value.
* Get the hardware ID.
* Get the hardware version.
* Get the firmware boot version.
* Get the firmware application version.
* Reset the device and return to boot mode.
* Update the application with binary file

Dependencies
=============

This driver has no dependency

Install
=======

Copy the python files in your project folder.

Usage Example
=============

The driver is split into several classes, because the methods and attributes available can be very different depending on the mode and operation.
To simplify use of the driver, a factory class (CCS811Factory) will select the right class to use for you, depending on the options you choose

Basic use in mode 1, 2 or 3 on wemos D1 mini:

.. code-block:: micropython

    import time
    from machine import Pin, I2C
    from ccs811factory import CCS811Factory

    ccs811 = CCS811Factory(I2C(scl=Pin(5), sda=Pin(4)))
    
    while True:
        if ccs811.data_is_ready:
            #ccs811.temperature = another_sensor.get_temp()
            #ccs811.humidity = another_sensor.get_hum()
            
            print(ccs811.eco2, "ppm and ", ccs811.etvoc, "ppb")
        time.sleep(1)

Use in mode 1, 2 or 3 with interrupt and thresholds on wemos D1 mini:

.. code-block:: micropython

    import time
    from machine import Pin, I2C
    from ccs811factory import CCS811Factory
    from ccs811 import CCS_MODE_3

    i2c = I2C(scl=Pin(5), sda=Pin(4))
    ccs811 = CCS811Factory(i2c, mode=CCS_MODE_3, with_int=True, with_thresh=True)
    #Change default values:
    ccs811.low_threshold = 800
    ccs811.high_threshold = 1000
    
    def data_is_ready(pin):
        print("warning: eCO2 ppm crosses a threshold!")
        print(ccs811.eco2, "ppm and ", ccs811.etvoc, "ppb")
    pin_int = Pin(0, Pin.IN, Pin.PULL_UP)
    pin_int.irq(data_is_ready, Pin.IRQ_FALLING)
    
    # Pin.IRQ_LOW_LEVEL is not available on wemos D1 mini,
    # so a first pass must be made if a value was already available
    # before the interrupt handler was set up.
    if not pin_int.value():
        data_is_ready(pin_int)
    
    while True:
        #ccs811.temperature = another_sensor.get_temp()
        #ccs811.humidity = another_sensor.get_hum()
        
        # Mode 3 – Low power pulse heating mode IAQ measurement every 60s
        time.sleep(60)
        
Use in mode 4 with wemos D1 mini:

.. code-block:: micropython

    import time
    from machine import Pin, I2C
    from ccs811factory import CCS811Factory
    from ccs811 import CCS_MODE_4

    i2c = I2C(scl=Pin(5), sda=Pin(4))
    ccs811 = CCS811Factory(i2c, mode=CCS_MODE_4)
    
    while True:
        if ccs811.data_is_ready:
            #ccs811.temperature = another_sensor.get_temp()
            #ccs811.humidity = another_sensor.get_hum()
            
            print(ccs811.voltage,"v and ",ccs811.current,"μA")
        time.sleep(0.25)


Documentation
=============

Read the code.

Contributing
============

Contributions are welcome!
