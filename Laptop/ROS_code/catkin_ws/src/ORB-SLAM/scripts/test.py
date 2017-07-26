#!/usr/bin/env python

# in this file we read frames from the RPI camera, convert them to
# sensor_msgs/Image and publish them on the topic camera/image_raw. This topic is
# read by the ORB-SLAM example script.

import roslib
import sys
import rospy
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

## to only publish a fixed image:
# if __name__ == '__main__':
#     rospy.init_node("test_node", anonymous=True)
#     image_pub = rospy.Publisher("camera/image_raw", Image, queue_size=10)
#     cv_bridge = CvBridge()
#
#     cv_image = cv2.imread("/home/fregu856/Desktop/test.png", -1)
#
#     rate = rospy.Rate(1) # (1 Hz)
#     while not rospy.is_shutdown():
#         img_ROS_msg = cv_bridge.cv2_to_imgmsg(cv_image, "mono8")
#         image_pub.publish(img_ROS_msg)
#         rate.sleep() # (to get loop frequency of 1 Hz)

if __name__ == '__main__':
    # initialize the ROS node:
    rospy.init_node("test_node", anonymous=True)

    # create publisher to publish frames from the vido stream:
    image_pub = rospy.Publisher("camera/image_raw", Image, queue_size=10)

    # initialize cv_bridge for conversion between openCV and ROS images:
    cv_bridge = CvBridge()

    # connect to the RPI video stream:
    cap = cv2.VideoCapture("tcp://172.24.1.1:8080")

    while not rospy.is_shutdown():
        # read the latest frame from the video stream:
        ret, frame = cap.read()
        img_cv = frame

        # # Display the resulting frame
        # cv2.imshow("test", img_cv)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

        # convert the video frame from openCV format to ROS format:
        img_ROS_msg = cv_bridge.cv2_to_imgmsg(img_cv, "rgb8")

        # publish the image in ROS format:
        image_pub.publish(img_ROS_msg)
