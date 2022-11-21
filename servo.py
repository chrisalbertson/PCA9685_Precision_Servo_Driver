"""control a set of hobby servos using PCA9685"""

import math
import pca9685

class servo:

	def __init__(self,log:bool=False):
		self.log = log
		self.angles = [0.0, 0.0, 0.0, 0.0,
					   0.0, 0.0, 0.0, 0.0,
					   0.0, 0.0, 0.0, 0.0,
					   0.0, 0.0, 0.0, 0.0]

		self.active = [False. False, False, False,
					   False. False, False, False,
					   False. False, False, False,
					   False. False, False, False]

		self.scale = [1.0, 1.0, 1.0, 1.0,
					  1.0, 1.0, 1.0, 1.0,
					  1.0, 1.0, 1.0, 1.0,
					  1.0, 1.0, 1.0, 1.0]

		self.bias =  [0.0, 0.0, 0.0, 0.0,
					  0.0, 0.0, 0.0, 0.0,
					  0.0, 0.0, 0.0, 0.0,
					  0.0, 0.0, 0.0, 0.0]


	def set_active(self, channel:int, state:bool=True):
		self.active[channel] = state

	def setup_servo(self, channel:int,

					"""NOTE.  I have decides to use a leave squares fit of a linear function"""

			  		state:bool=True,
			  		range_deg:float=180.0,	# servo's nominal range
			  		usec_min = 1000.0,
			  		usec_max = 2000.0,
			  		usec_at_calibration,
			  		radians_at_calibration):

		self.set_active(channel, state)

		range_radian = range_deg * (math.pi / 180.0)
		range_usec = usec_max - usec_min
		usec_per_radian = range_usec / range_radian

	def set_radian(self, channel:int, rad:float):
		self.angles[channel] = rad

	def set_radian_range(self, start_channel:int, rads):
		end = start_channel + len(rads)
		self.angles[start_channel:end]=rads

	def write_all(self):
		pwm = (self.scale * self.angles) + self.bias
		for channel in range(16):
			if self.active[channel]:
				pca.write(channel, pwm[channel])


	def print_state(self):
		print('angles ',self.angles)
		print('angles ',self.active)

