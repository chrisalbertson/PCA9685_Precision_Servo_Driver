"""Demo program to show and test the server driver"""

import time
import numpy as np
import math
import servo

s = servo.Servo()


def main():

    midpoint = 90.0
    peak = 10.0
    angles = np.array([midpoint for i in range(16)])

    movement_period = 2.0
    loop_period = 1.0/20.0

    # To prevent a large current draw on the power supply, move the motors
    # one at a time to the neutral position.
    for ch in range(16):
        s.move_radian(ch, midpoint)
        time.sleep(0.25)

    # Move motors slowly around the midpoint
    start_time = time.time()
    while True:
        tick = time.time()
        phase_angle = 2.0 * math.pi * (((tick - start_time) % movement_period) / movement_period)

        s.move_16_radian(angles + (peak * math.sin(phase_angle)))

        time.sleep(loop_period - (time.time()-tick))

if __name__ == '__main__':
    main()
