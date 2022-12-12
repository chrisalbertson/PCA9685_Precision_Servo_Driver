# FSA_PCA9685_Servo_Driver
A fast, simple and accurate servo driver using the PCA9685.
## About
NOTICE: *This software is **not finished** and not ready for use.
I'm still writing it.*

The PCA9685 breakout board as designed and sold by Adafriut is a great way to control up to 16 hobby-style servo motors but the existing software drivers I could find were at bit slow and did not offer calibration for as-built assembly. This driver is written in pure python and tries to be as fast and simple as possible.

This driver is based on the driver supplied with varius robots made and sold by Freenove..  Files were cloned from their github repository and used as a starting point for this work.

This software was made by Chris Albertson albertson.chris@gmail.com in late 2022.   It is provided for you use in any open source project.  There is no warenty. if it is broken you may keep the pieces or try to repair them yourself.

## Features
1) While not required, the driver assume the user is running a control loop that runs several times per second (perhaps at 20 to 40 Hz) and that all servos will be updated at the same time.  The driver design is optimized for this use case.
2) A user level GUI application is provided to make the calibration process easy.  Using this app, the servo can be command to any position.  Then the actual angle the robot part moved to can be measured and this data entered into the app.  Any number of calibration points may be entered.  The app uses this data to create a calibration file.
3) The real-time servo drives uses the data from the calibration file to correct any error inherent t the servo and for as-built error in the robot assembly
4) All calculations are done using Python's Numy package.  The real-time driver accepts angles in radians and these are directly converted to microseconds using the fitted calibration function.  The calculation is streamlined and made fast be using Numpy fr all calculations

## How to install and use this software
## Resources.
other drivers
https://github.com/dheera/ros-pwm-pca9685/blob/master/pwm_pca9685/src/pca9685_activity.cpp

