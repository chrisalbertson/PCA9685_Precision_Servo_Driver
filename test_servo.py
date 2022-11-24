import time
import servo

s = servo.Servo()


def main():
    s.move_radian(0, 3.14159/2.0)
    """while True:
        time.sleep(1.0)
        s.set_degrees(0, 70.0)
        time.sleep(0.5)
        s.set_degrees(0, 110.0)"""

if __name__ == '__main__':
    main()
