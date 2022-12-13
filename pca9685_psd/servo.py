"""control a set of hobby servos using PCA9685"""

import logging
import math

import yaml
import numpy as np
import pca9685_psd


class Servo:
	"""Control up to 16 servos connected to a PCA9685 with calibration and limit checks."""

	def __init__(self,
                 smbus_number: int = 1,
				 log: bool = False,
				 noi2c: bool = False):

		self.log = log

		names            = []
		slope_list       = []
		intercept_list   = []
		lower_limit_list = []
		upper_limit_list = []

		with open('servo_cal.yaml', mode="rt", encoding="utf-8") as cal_file:
			cal_data = yaml.safe_load(cal_file)

		for chan in cal_data:
			names.append(cal_data[chan]['name'])
			slope_list.append(cal_data[chan]['slope'])
			intercept_list.append(cal_data[chan]['intercept'])
			lower_limit_list.append(cal_data[chan]['usec lower limit'])
			upper_limit_list.append(cal_data[chan]['usec upper limit'])

		self.names       = names
		self.slope       = np.array(slope_list)
		self.intercept   = np.array(intercept_list)
		self.lower_limit = np.array(lower_limit_list)
		self.upper_limit = np.array(upper_limit_list)

		# This is a list of the active channel numbers
		active_list = []
		for ch_indx in range(16):
			if cal_data[chan]['active']:
				active_list.append(ch_indx)

		if not noi2c:
			self.pca = pca9685.PCA9685(smbus_number=smbus_number,
									   bus_frequency=50.0,
									   active_channels=active_list)


	def move_16_radian(self, radians):
		"""Move all active servos to angles expressed in radians."""

		usecs = (self.slope * clipped) + self.intercept
		usecs_clipped = np.fmin(np.fmax(usecs, self.lower_limit), self.upper_limit)

		self.pca.goto_16_usec(usecs_clipped)

	def move_16_radian_nolimit(self, radians):
		"""Move all active servos to angles expressed in radians, with no limit checks."""

		usecs = (self.slope * radians) + self.intercept
		self.pca.goto_16_usec(usecs)


	def move_radian(self, channel_number, radian):
		"""Move a servo to an angle expressed in radians."""

		usec = (self.slope[channel_number] * clipped) + self.intercept[channel_number]
		usec_clipped = min(max(usec, self.lower_limit[channel_number]), self.upper_limit[channel_number])
		self.pca.goto_usec(channel_number, usec_clipped)


	def move_radian_nolimit(self, channel_number, radian):
		"""Move a servo to an angle expressed in radians, with no limit checks."""

		usec = (self.slope[channel_number] * radian) + self.intercept[channel_number]
		self.pca.goto_usec(channel_number, usec)


	def move_usec(self, channel_number, usec):
		"""Move a servo to an angle expressed in microseconds, with no limit checks."""

		self.pca.goto_usec(channel_number, usec)

	def radian_to_usec(self, channel_number, radian) -> float:

		usec = (self.slope[channel_number] * radian) + self.intercept[channel_number]
		return usec

	def usec_to_radian(self, channel_number, usec) -> float:

		radian =(usec - self.intercept[channel_number]) / self.slope[channel_number]
		return radian


if __name__ == '__main__':
	"""Do a Hello World test to verify everything is working."""

	import time
	import numpy as np
	import yappi

	yappi.start()

	s = servo.Servo()

	# Move servos one at a time
	for angle in (0, 10, 0, -10, 0):
		for chan in range(16):
			s.move_radian(chan, math.radians(angle))
			time.sleep(0.2)
		time.sleep(1)

	# Move servos 16 at a time
	angle0 = np.array([0.0 for i in range(16)])
	delta = math.radians(10.0)
	for i in range(5):
		s.move_16_radian(angle0)
		time.sleep(0.2)
		s.move_16_radian(angle0+delta)
		time.sleep(0.2)
		s.move_16_radian(angle0)
		time.sleep(0.2)
		s.move_16_radian(angle0-delta)
		time.sleep(0.2)

	yappi.get_func_stats().print_all()
	yappi.get_thread_stats().print_all()
