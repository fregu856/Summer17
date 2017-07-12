import socket
from threading import Thread
import time
import Adafruit_PCA9685

global cycles_without_web_contact, mode, manual_state

cycles_without_web_contact = 0
mode = "Manual" # (mode is either "Manual" or "Auto")
throttle_direction = "No_throttle" # (throttle_direction is either "No_throttle", "Forward" or "Backward")
steering_direction = "No_steering" # (steering_direction is either "No_steering", "Right or "Left")
throttle = 0
steering_angle = 0

throttle_max = 0.35 # (actually, the max is 1, but we limit the speed)
throttle_min = -0.4 # (actually, the min is -1, but we limit the speed)
throttle_max_physical = 1
throttle_min_physical = -1
steering_angle_max = 1
steering_angle_min = -1

def linear_interp(x_val, x_min, x_max, y_min, y_max):
    x_range = x_max - x_min
    y_range = y_max - y_min
    xy_ratio = float(x_range)/float(y_range)

    y = (x_val-x_min)/xy_ratio + y_min

    return int(y)

def comm_thread():
    global cycles_without_web_contact, mode, throttle_direction, steering_direction
    global throttle, steering_angle

    # create a TCP/IP socket:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = "172.24.1.1" # (RPI IP address)
    port = 9999

    # bind to the port:
    server_socket.bind((host, port))

    # queue up to 10 requests:
    server_socket.listen(10)

    # wait for the client to connect and receive its transmitted messages (we will
    # run one entire cycle of the while loop everytime the client sends something):
    while True:
        # establish a connection with the client:
        connection, client_address = server_socket.accept()

        # receive the message from the client (no more than 4096 bytes, all messages
        # from the client should always be shorter than this):
        message = connection.recv(4096)

        if message in ["Manual", "Auto"]:
            # the client sent an updated mode, update 'mode':
            mode = message
        elif message in ["No_throttle", "Forward", "Backward"]:
            # the client sent an updated throttle directon, update 'throttle_direction':
            throttle_direction = message
        elif message in ["No_steering", "Right", "Left"]:
            # the client sent an updated steering direction, update 'steering_direction':
            steering_direction = message
        elif message == "control_ping":
            # the client sent a connection control ping, reset the counter:
            cycles_without_web_contact = 0
        else:
            msg_type, msg_value_string = message.split(":")
            if msg_type == "Throttle":
                throttle = float(msg_value_string)
            elif msg_type == "Steering angle":
                steering_angle = float(msg_value_string)
            else:
                print "##############################"
                print "##############################"
                print "##############################"
                print "Received data of unknown type!"
                print "##############################"
                print "##############################"
                print "##############################"

        connection.close()

def control_thread():
    global cycles_without_web_contact, steering_angle, throttle

    global braking, recently_reversed

    braking = False
    recently_reversed = False

    throttle_channel = 0 # (the motor is connected to channel 0 on the pwm driver)
    steering_channel = 1 # (the steering servo is connected to channel 1 on the pwm driver)
    pwm_frequency = 60 # (60 Hz is a standard choice for servos)

    left_pulse = 490 # (pwm pulse length corr. to maximum left turn)
    right_pulse = 330 # (pwm pulse length corr. to maximum right turn)
    straight_pulse = 410 # (pwm pulse length corr. to 0 steering angle)

    min_pulse = 300 # (pwm pulse length corr. to maximum reverse throttle)
    max_pulse = 500 # (pwm pulse length corr. to maximum forward throttle)
    zero_pulse = 400 # (pwm pulse length corr. to zero throttle)

    # initialise the PCA9685 using the default address (0x40).
    driver = Adafruit_PCA9685.PCA9685()
    # set the PWM frequency:
    driver.set_pwm_freq(pwm_frequency)

    while True:
        cycles_without_web_contact += 1
        if cycles_without_web_contact > 5:
            # if we havn't had wifi contact with the client for ~ 0.25 sec, stop the robot:
            stop_runaway_car()

        ########################################################################
        # steering:
        # # convert manual steering commands to a steering angle:
        if steering_direction == "Right":
            if steering_angle < -0.001:
                # quickly increase the steering angle from negative (left) towards 0:
                steering_angle = steering_angle + 0.2
            else:
                # increase the steering angle slightly (steer more to the right):
                steering_angle = steering_angle + 0.2
        elif steering_direction == "Left":
            # quickly decrease the steering angle from positive (right) towards 0:
            if steering_angle > 0.001:
                steering_angle = steering_angle - 0.2
            else:
                # decrease the steering angle slightly (steer more to the left):
                steering_angle = steering_angle - 0.2
        elif steering_direction == "No_steering": # (if the user is not pressing Forward nor Backward):
            if steering_angle > 0.001:
                # quickly decrease the steering angle from positive (right) towards 0:
                if steering_angle < 0.2:
                    steering_angle = steering_angle - 0.1
                else:
                    steering_angle = steering_angle - 0.2
            elif steering_angle < -0.001:
                # quickly increase the steering angle from negative (left) towards 0:
                if steering_angle > -0.2:
                    steering_angle = steering_angle + 0.1
                else:
                    steering_angle = steering_angle + 0.2

        # # limit the steering angle to [steering_angle_min, steering_angle_max]:
        if steering_angle > steering_angle_max:
            steering_angle = steering_angle_max
        elif steering_angle < steering_angle_min:
            steering_angle = steering_angle_min

        # # convert steering_angle to the corr. pwm pulse length via linear interpolation:
        if steering_angle > 0:
            steering_angle_pulse = linear_interp(steering_angle, 0,
                        steering_angle_max, straight_pulse, right_pulse)
        elif steering_angle < 0:
            steering_angle_pulse = linear_interp(steering_angle, steering_angle_min,
                        0, left_pulse, straight_pulse)
        else:
            steering_angle_pulse = straight_pulse

        # # set the pwm pulse length on the steering channel to steering_angle_pulse
        # # (this is what actually makes the steering servo move):
        driver.set_pwm(steering_channel, 0, steering_angle_pulse)

        ########################################################################
        # throttle:
        # # convert manual throttle commands to a throttle:
        if throttle_direction == "Forward":
            if throttle < -0.001: # (if currently reversing:)
                # set the throttle to 0 to quickly make the car stop reversing:
                throttle = 0
            else:
                if throttle >= throttle_max:
                    recently_reversed = False
                # increase the throttle slightly (more forward throttle):
                throttle = throttle + 0.025
            braking = False
        elif throttle_direction == "Backward":
            if throttle > 0.001 and not recently_reversed: # (if currently driving forward:)
                # apply maximum braking force (on our specific RC car at least,
                # going from positive to negative throttle once will stop the forward
                # motion but not put into reverse. To stop a forward motion and then
                # start reversing, one needs to first apply a negative throttle, let
                # the throttle go back to 0 and then apply a negative throttle again):
                throttle = -1
                braking = True
            else:
                # decrease the throttle slightly (more reverse throttle):
                throttle = throttle - 0.025
                if throttle > -1:
                    braking = False
                    recently_reversed = True
        elif throttle_direction == "No_throttle":
            if throttle > 0.001:
                # decrease the throttle slightly from positive (forward) towards 0:
                throttle = throttle - 0.025
            elif throttle < -0.001:
                # increase the throttle slightly from negative (reverse/braking) towards 0:
                throttle = throttle + 0.025
            braking = False

        # # limit the throttle:
        if not braking:
            # limit the throttle to [throttle_min, throttle_max]:
            if throttle > throttle_max:
                throttle = throttle_max
            elif throttle < throttle_min:
                throttle = throttle_min
        else: # (if currently braking the car:)
            # allow throttle = -1 (maximum braking force):
            if throttle > throttle_max:
                throttle = throttle_max
            elif throttle < throttle_min_physical:
                throttle = throttle_min_physical

        # # convert throttle to the corr. pwm pulse length via linear interpolation:
        throttle_pulse = linear_interp(throttle, -1, 1, min_pulse, max_pulse)

        # # set the pwm pulse length on the throttle channel to throttle_pulse
        # # (this is what actually makes the motor increase/decrease speed):
        driver.set_pwm(throttle_channel, 0, throttle_pulse)

        # print all relevant info:
        print "mode: %s" % mode
        print "throttle direction: %s" % throttle_direction
        print "steering direction: %s" % steering_direction
        print "throttle: %f" % throttle
        print "throttle pulse: %f" % throttle_pulse
        print "steering angle: %f" % steering_angle
        print "steering angle pulse: %f" % steering_angle_pulse
        print cycles_without_web_contact

        # delay for 0.05 sec (for ~ 20 Hz loop frequency):
        time.sleep(0.05)

def stop_runaway_car():
    global mode, throttle, steering_angle
    global throttle_direction, steering_direction, braking

    # set all variables to make the car stop:
    mode = "manual"
    if throttle > 0.001: # (if currently moving forward:)
        # brake the car:
        throttle_direction = "Backward"
    elif braking: # (if currently braking the car:)
        # keep braking the car:
        throttle_direction = "Backward"
    else:
        throttle_direction = "No_throttle"
    steering_direction = "No_steering"

# start a thread that constantly reads messages from the client:
thread_comm = Thread(target = comm_thread)
thread_comm.start()

# start a thread that converts the read messages to commands for the steering
# servo and motor, and constantly checks if we have lost wifi connection with the client:
thread_control = Thread(target = control_thread)
thread_control.start()
