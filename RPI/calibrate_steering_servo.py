# NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE!
# This code is modeled after scripts/calibrate.py in https://github.com/wroscoe/donkey
# NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE!

# Run this script to test what PWM pulse values will work for the car's steering
# control. When you run the script, you'll be prompted to enter PWM test values.
# Start at 400 and note the resulting steering angle. Then increase/decrease the
# value until you find the value corresponding to maximum steering to the left
# (left_pulse) and to the right (right_pulse). For reference, I got
# left_pulse = 510 and right_pulse = 310.

import Adafruit_PCA9685

channel = 1 # (1: steering servo, 0: throttle)
pwm_frequency = 60 # (60 Hz is a standard choice for servos)

# initialise the PCA9685 using the default address (0x40).
driver = Adafruit_PCA9685.PCA9685()
# set the PWM frequency:
driver.set_pwm_freq(pwm_frequency)

for i in range(10):
	# ask the user for a new PWM pulse value:
	pwm_pulse = int(input("What PWM pulse setting? "))
	# set the provided PWM pulse:
	driver.set_pwm(channel, 0, pwm_pulse)
