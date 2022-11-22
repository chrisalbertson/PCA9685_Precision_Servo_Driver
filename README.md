# FSA_PCA9685_Servo_Driver
A fast, simple and accurate servo driver using the PCA9685.
## About
NOTICE: *This software is **not finished** and not ready for use.
I'm still writing it.*

The PCA9685 breakout board as designed and sold by Adafriut is a great way to control up to 16 hobby-style servo motors but the existing software drivers I could find were at bet slow and did not offer calibration for as-built assembly. This driver is written in pure python and tries to be as fast and simple as possible.

This driver is based on the driver supplied with varius robots made and sold by Freenove..  Files were cloned from their github repository and used as a starting point for this work

This software was made by Chris Albertson albertson.chris@gmail.com in late 2022.   It is provided for you use in any open source project.  There is no warenty, if it is broken you may keep the pieces or try to repair them yourself.

## Features
1) While not required, the driver assume the user is running a control loop that runs several times per second (perhaps at 20 to 40 Hz) and that all servos will be updated at the same time.  Th driver design is optimized for this use case
2) I user level GIU application is provided to make the calibration process easy and foolproof.
3) Provision is made for very accurate as-built calibration.  The user can send the servo an specici pulse length and then measure to actual angle.  A linear calibration funtion is fit to any number of these measurements and then used durring real-time operations.  This can hep average out errors in angle meauremtna dngear backlash
4) All calculations are done using Python's Numy package.  This is the fastest way.
5) angles are accepted in radians and are directly converted to microseconds using the fitted calibration funtion with only one multiley and one addition.

## How to instal and use this software
## Resources.
