"""PCA9685 16-Channel PWM Servo Driver"""

import time
import math

"""
We can use either the smbus or subus2 package.
Be sure the used is a member of the i2c group
"""
import smbus
#import smbus2 as smbus

from collections.abc import Sequence

class PCA9685:

    # Registers/etc.
    __SUBADR1            = 0x02
    __SUBADR2            = 0x03
    __SUBADR3            = 0x04
    __MODE1              = 0x00
    __PRESCALE           = 0xFE
    __LED0_ON_L          = 0x06
    __LED0_ON_H          = 0x07
    __LED0_OFF_L         = 0x08
    __LED0_OFF_H         = 0x09
    __ALLLED_ON_L        = 0xFA
    __ALLLED_ON_H        = 0xFB
    __ALLLED_OFF_L       = 0xFC
    __ALLLED_OFF_H       = 0xFD

    delay = 0.025

    def __init__(self,
                 smbus_number: int = 1,
                 address: int = 0x40,
                 bus_frequency: float = 60.0,
                 active_channels: list[int] = [c for c in range(16)],
                 clock_correction = 0.920):

        self.address = address
        self.active_channels = active_channels.copy()
        self.bus_frequency = bus_frequency
        self.bus_period_usec = (1.0 / bus_frequency) * 1000000.0
        
        # To find clock_correction, set it to 1.0 then mesure width of a 1 ms pulse
        # if the actual width is (say) 0.950 ms then set clock corection to 0.950
        # when the corect is corect a 1000 uSec pulse will measure to within
        # about 1% of 1000 uSec.  We can not get closer because "prescale" must
        # be an integer
        self.clock_correction = clock_correction


        self.bus = smbus.SMBus(smbus_number)
        time.sleep(self.delay)

        self.write(self.__MODE1, 0x00)
        time.sleep(self.delay)

        self.setPWMFreq(bus_frequency)
        time.sleep(self.delay)

        self.last_off: list[int] = [0     for i in range(16)]
        self.on2zero: list[bool] = [False for i in range(16)]
    
    def write(self, reg: int, value: int) -> None:
        """"Writes an 8-bit value to the specified register/address."""
        time.sleep(0.0001)
        self.bus.write_byte_data(self.address, reg, value)
      
    def read(self, reg: int) -> int:
        """Read an unsigned byte from the I2C device."""
        result = self.bus.read_byte_data(self.address, reg)
        return result
    
    def setPWMFreq(self, freq: float) -> None:
        """Set the PWM frequency."""

        prescaleval = 25000000.0 / self.clock_correction   # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        prescale = math.floor(prescaleval + 0.5)
        
        # print('PCA9685 using prescale value = ', prescale, '  freq =', freq)

        # oldmode = self.read(self.__MODE1)
        #newmode = (oldmode & 0x7F) | 0x10        # sleep
        self.write(self.__MODE1, 0x10)        # go to sleep
        time.sleep(self.delay)

        self.write(self.__PRESCALE, int(prescale))
        time.sleep(self.delay)

        self.write(self.__MODE1, 0x00)
        time.sleep(self.delay)

        """self.write(self.__MODE1, oldmode)
        time.sleep(self.delay)

        self.write(self.__MODE1, oldmode | 0x80)
        time.sleep(self.delay)"""

    """
    def setPWM(self, channel, on, off):
        "Sets a single PWM channel"
        self.write(self.__LED0_ON_L+4*channel, on & 0xFF)
        self.write(self.__LED0_ON_H+4*channel, on >> 8)
        self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
        self.write(self.__LED0_OFF_H+4*channel, off >> 8)


    def setMotorPwm(self,channel,duty):
        self.setPWM(channel,0,duty)

    def setServoPulse(self, channel, pulse):
        "Sets the Servo Pulse,The PWM frequency must be 50HZ"
        pulse = pulse*4096/20000        #PWM frequency is 50HZ,the period is 20000us
        self.setPWM(channel, 0, int(pulse))
    """

    def goto_usec(self, channel: int, usec: float) -> None:
        """Update the pulse width on the specified channel."""

        # self.setServoPulse(channel, usec)
        off: int = round(usec * (4096.0 / self.bus_period_usec))
        chanx4: int = 4 * channel
        try:
            self.write(self.__LED0_ON_L  + chanx4, 0)
            self.write(self.__LED0_ON_H  + chanx4, 0)
            self.write(self.__LED0_OFF_L + chanx4, off & 0xFF)
            self.write(self.__LED0_OFF_H + chanx4, off >> 8)
        except:
            print('WARNING, goto_usec() write failed')

    def goto_16_usec(self, usec_array: Sequence[float]) -> None:
        """Update the pulse widths on up to 16 channels."""
        #print('goto_16_usec', usec_array)
        for chan_indx in self.active_channels:

            off: int = round(usec_array[chan_indx] * (4096.0 / self.bus_period_usec))

            if self.last_off[chan_indx] == off:
                continue

            self.last_off[chan_indx] = off
            chanx4: int = 4 * chan_indx
            try:
                if not self.on2zero[chan_indx]:
                    self.write(self.__LED0_ON_L  + chanx4, 0)
                    self.write(self.__LED0_ON_H  + chanx4, 0)
                    self.on2zero[chan_indx] = True
                self.write(self.__LED0_OFF_L + chanx4, off & 0xFF)
                self.write(self.__LED0_OFF_H + chanx4, off >> 8)
            except:
                print('WARNING, goto_16_usec() write failed, retrying once...')
                self.goto_usec(chan_indx, usec_array[chan_indx])



def __test_pca() -> None:
    """Do a Hello World test to verify everything is working."""

    import numpy as np
    import yappi

    yappi.start()

    moving_chans = [0, 4]   # list of servo channels to move
    pulse_center = 1500     # microseconds
    delta = 20              # microseconds
    delay = 1.0/2.0         # 2Hz

    pca = PCA9685(active_channels=moving_chans)

    us_list_hi     = np.array([pulse_center for i in range(16)])
    us_list_low    = np.array([pulse_center for i in range(16)])
    for ch in moving_chans:
        us_list_hi[ch]  += delta
        us_list_low[ch] -= delta

    for i in range(100):
        time.sleep(delay)
        pca.goto_16_usec(us_list_hi)
        time.sleep(delay)
        pca.goto_16_usec(us_list_low)

    yappi.get_func_stats().print_all()
    yappi.get_thread_stats().print_all()


if __name__ == '__main__':
    import sys

    try:
        __test_pca()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)

