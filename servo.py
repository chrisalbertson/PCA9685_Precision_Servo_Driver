"""control a set of hobby servos using PCA9685"""

import logging
import yaml
import numpy as np
import pca9685

class Servo:

	def __init__(self,log:bool=False):
		self.log = log

		self.pca = pca9685.PCA9685

		active_list      = []
		names            = []
		slope_list       = []
		intercept_list   = []
		lower_limit_list = []
		upper_limit_list = []

		with open('servo_cal.yaml', mode="rt", encoding="utf-8") as file:
			cal_data = yaml.safe_load(file)

		for chan in cal_data:
			active_list.append(cal_data[chan]['active'])
			names.append(cal_data[chan]['name'])
			slope_list.append(cal_data[chan]['slope'])
			intercept_list.append(cal_data[chan]['intercept'])
			lower_limit_list.append(cal_data[chan]['angle lower limit'])
			upper_limit_list.append(cal_data[chan]['angle upper limit'])

		self.active      = np.array(active_list)
		self.names       = names
		self.slope       = np.array(slope_list)
		self.intercept   = np.array(intercept_list)
		self.lower_limit = np.array(lower_limit_list)
		self.upper_limit = np.array(upper_limit_list)


	def move_16_radian(self, radians):
		clipped = np.amin(np.amax(radians, self.lower_limit), self.upper_limit)
		usecs = (self.slope * clipped) + self.intercept
		self.pca.goto_16_usec(usecs)

	def move_16_radian_nolimit(self, radians):
		usecs = (self.slope * radians) + self.intercept
		self.pca.goto_16_usec(usecs)


	def move_radian(self, channel_number, radian):
		clipped = min(max(radian, self.lower_limit[channel_number]), self.upper_limit[channel_number])
		usec = (self.slope[channel_number] * clipped) + self.intercept[channel_number]
		self.pca.goto_usec(usec)


	def move_radian_nolimit(self, channel_number, radian):
		usec = (self.slope[channel_number] * radian) + self.intercept[channel_number]
		pca.goto_usec(usec)
