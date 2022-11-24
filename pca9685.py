"""PCA9685 16-Channel PWM Servo Driver"""

import time
import math
import smbus


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

    def __init__(self, address: int = 0x40,
                       bus_frequency: float = 50.0,
                       active_channels: list = range(16)):

        self.bus = smbus.SMBus(1)
        self.address = address
        self.active_channels = active_channels.copy()

        self.write(self.__MODE1, 0x00)
        self.setPWMFreq(bus_frequency)

    
    def write(self, reg, value):
        "Writes an 8-bit value to the specified register/address"
        self.bus.write_byte_data(self.address, reg, value)
      
    def read(self, reg):
        "Read an unsigned byte from the I2C device"
        result = self.bus.read_byte_data(self.address, reg)
        return result
    
    def setPWMFreq(self, freq):
        "Sets the PWM frequency"
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        prescale = math.floor(prescaleval + 0.5)

        oldmode = self.read(self.__MODE1)
        newmode = (oldmode & 0x7F) | 0x10        # sleep
        self.write(self.__MODE1, newmode)        # go to sleep
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)

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


    def goto_usec(self, channel, usec):

        # self.setServoPulse(channel, usec)
        off = int(usec*4096/20000)
        chanx4 = 4 * channel
        self.write(self.__LED0_ON_L  + chanx4, 0)
        self.write(self.__LED0_ON_H  + chanx4, 0)
        self.write(self.__LED0_OFF_L + chanx4, off & 0xFF)
        self.write(self.__LED0_OFF_H + chanx4, off >> 8)

    def goto_16_usec_x(self, usec_array):
        for chan_indx, usec in enumerate(usec_array):
            self.goto_usec(chan_indx, usec)

    def goto_16_usec_x(self, usec_array):
        for chan_indx in range(16):
            self.goto_usec(chan_indx, usec_array[chan_indx])

    def goto_16_usec(self, usec_array):
        for chan_indx in self.active_channels:
            off = int(usec_array[chan_indx] * 4096 / 20000)
            chanx4 = 4 * chan_indx
            self.write(self.__LED0_ON_L  + chanx4, 0)
            self.write(self.__LED0_ON_H  + chanx4, 0)
            self.write(self.__LED0_OFF_L + chanx4, off & 0xFF)
            self.write(self.__LED0_OFF_H + chanx4, off >> 8)



if __name__ == '__main__':
    """Do a Hello World test to verify everything is working."""

    import numpy as np
    import yappi

    yappi.start()

    moving_chans = [0, 4]
    pulse_center = 1500
    delta = 20
    delay = 1.0/4.0

    pca = PCA9685(active_channels=moving_chans)

    us_list_hi     = np.array([pulse_center for i in range(16)])
    us_list_low    = np.array([pulse_center for i in range(16)])
    for ch in moving_chans:
        us_list_hi[ch]  = pulse_center + delta
        us_list_low[ch] = pulse_center - delta

    for i in range(100):
        time.sleep(delay)
        pca.goto_16_usec(us_list_hi)
        time.sleep(delay)
        pca.goto_16_usec(us_list_low)

    yappi.get_func_stats().print_all()
    yappi.get_thread_stats().print_all()
