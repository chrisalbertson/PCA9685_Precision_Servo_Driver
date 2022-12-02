"""control a set of hobby servos using PCA9685"""

import logging
import yaml
import numpy as np
import pca9685
import servo


class Servo:
	"""Control up to 16 servos connected to a PCA9685 with calibration and limit checks."""

	def __init__(self,
				 log: bool = False):

		self.log = log

		names            = []
		slope_list       = []
		intercept_list   = []
		lower_limit_list = []
		upper_limit_list = []

		with open('servo_cal.yaml', mode="rt", encoding="utf-8") as file:
			cal_data = yaml.safe_load(file)

		for chan in cal_data:
			names.append(cal_data[chan]['name'])
			slope_list.append(cal_data[chan]['slope'])
			intercept_list.append(cal_data[chan]['intercept'])
			lower_limit_list.append(cal_data[chan]['angle lower limit'])
			upper_limit_list.append(cal_data[chan]['angle upper limit'])

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

		self.pca = pca9685.PCA9685(bus_frequency=50.0,
								   active_channels=active_list)


	def move_16_radian(self, radians):
		"""Move all active servos to angles expressed in radians."""

		clipped = np.fmin(np.fmax(radians, self.lower_limit), self.upper_limit)
		usecs = (self.slope * clipped) + self.intercept
		self.pca.goto_16_usec(usecs)

	def move_16_radian_nolimit(self, radians):
		"""Move all active servos to angles expressed in radians, with no limit checks."""

		usecs = (self.slope * radians) + self.intercept
		self.pca.goto_16_usec(usecs)


	def move_radian(self, channel_number, radian):
		"""Move a servo to an angle expressed in radians."""

		clipped = min(max(radian, self.lower_limit[channel_number]), self.upper_limit[channel_number])
		usec = (self.slope[channel_number] * clipped) + self.intercept[channel_number]
		self.pca.goto_usec(channel_number, usec)


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
	for angle in (90, 100, 90, 80, 90):
		for chan in range(16):
			s.move_radian(chan, angle)
			time.sleep(0.2)
		time.sleep(1)

	# Move servos 16 at a time
	angle90 = np.array([90.0 for i in range(16)])
	for i in range(5):
		s.move_16_radian(angle90)
		time.sleep(0.2)
		s.move_16_radian(angle90+10.0)
		time.sleep(0.2)
		s.move_16_radian(angle90)
		time.sleep(0.2)
		s.move_16_radian(angle90-10.0)
		time.sleep(0.2)

	yappi.get_func_stats().print_all()
	yappi.get_thread_stats().print_all()