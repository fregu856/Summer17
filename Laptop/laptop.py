###########################################################################
# MultiNet imports START:
###########################################################################
# from __future__ import absolute_import
# from __future__ import division
# from __future__ import print_function
# import json
# import logging
# import os
# import sys
# import collections
# import cv2
# import numpy as np
# import scipy as scp
# import scipy.misc
# import tensorflow as tf
# import time
# from PIL import Image, ImageDraw, ImageFont
#
# # add the "TensorVision" dir to the path so that its content can be imported:
# import sys
# sys.path.append("/home/fregu856/Zenuity/MultiNet/submodules/TensorVision")
# import tensorvision.utils as tv_utils
# import tensorvision.core as core
###########################################################################
# MultiNet imports END:
###########################################################################


import numpy as np
import cv2
import requests
from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
import time
from threading import Thread
import socket
from darkflow.net.build import TFNet

# def _to_color(indx, base):
#     """
#         return (b, r, g) tuple
#         (function taken from darkflow)
#     """
#     base2 = base * base
#     b = 2 - indx / base2
#     r = 2 - (indx % base2) / base
#     g = 2 - (indx % base2) % base
#     return (b * 127, r * 127, g * 127)

def send_to_RPI(message):
    # create a TCP/IP socket:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to the RPI server:
    host = "172.24.1.1" # (RPI IP address)
    port = 9999
    client_socket.connect((host, port))

    # send the message:
    client_socket.sendall(message)

    # close the socket:
    client_socket.close()

# # YOLO class labels:
# labels = ["aeroplane", "bicycle", "bird", "boat", "bottle",
#     "bus", "car", "cat", "chair", "cow", "diningtable", "dog",
#     "horse", "motorbike", "person", "pottedplant", "sheep", "sofa",
#     "train", "tvmonitor"]
#
# # assign a unique color to each YOLO class label (for bounding boxes):
# colors = []
# base = int(np.ceil(pow(len(labels), 1./3)))
# for x in range(len(labels)):
# 	colors += [_to_color(x, base)]
#
# # load the pretrained tiny-YOLO network:
# options = {"model": "/home/fregu856/darkflow/cfg/tiny-yolo-voc.cfg",
#             "load": "/home/fregu856/darkflow/bin/tiny-yolo-voc.weights",
#             "threshold": 0.2}
# tiny_YOLO_net = TFNet(options)
# print ("Everything YOLO-related is loaded!")

throttle_direction = "No_throttle"
steering_direction = "No_steering"
mode = "Manual"
steering_angle = 0
throttle = 0

latest_video_frame = []
latest_video_frame_small = []
latest_video_frame_right = []
latest_video_frame_small_right = []
latest_video_frame_left = []
latest_video_frame_small_left = []


###########################################################################
# MultiNet START:
###########################################################################
# default_run = 'MultiNet_ICCV'
# weights_url = ("ftp://mi.eng.cam.ac.uk/"
#                "pub/mttt2/models/MultiNet_ICCV.zip")
#
# def load_united_model(logdir):
#     subhypes = {}
#     subgraph = {}
#     submodules = {}
#     subqueues = {}
#
#     first_iter = True
#
#     meta_hypes = tv_utils.load_hypes_from_logdir(logdir, subdir="",
#                                                  base_path='hypes')
#     for model in meta_hypes['models']:
#         subhypes[model] = tv_utils.load_hypes_from_logdir(logdir, subdir=model)
#         hypes = subhypes[model]
#         hypes['dirs']['output_dir'] = meta_hypes['dirs']['output_dir']
#         hypes['dirs']['image_dir'] = meta_hypes['dirs']['image_dir']
#         submodules[model] = tv_utils.load_modules_from_logdir(logdir,
#                                                               dirname=model,
#                                                               postfix=model)
#
#         modules = submodules[model]
#
#     image_pl = tf.placeholder(tf.float32)
#     image = tf.expand_dims(image_pl, 0)
#     image.set_shape([1, 384, 1248, 3])
#     decoded_logits = {}
#
#     for model in meta_hypes['models']:
#         hypes = subhypes[model]
#         modules = submodules[model]
#         optimizer = modules['solver']
#
#         with tf.name_scope('Validation_%s' % model):
#             reuse = {True: False, False: True}[first_iter]
#
#             scope = tf.get_variable_scope()
#
#             with tf.variable_scope(scope, reuse=reuse):
#                 logits = modules['arch'].inference(hypes, image, train=False)
#
#             decoded_logits[model] = modules['objective'].decoder(hypes, logits,
#                                                                  train=False)
#
#         first_iter = False
#
#     sess = tf.Session()
#     saver = tf.train.Saver()
#     cur_step = core.load_weights(logdir, sess, saver)
#
#     return meta_hypes, subhypes, submodules, decoded_logits, sess, image_pl
#
#
# tv_utils.set_gpus_to_use()
#
# runs_dir = "/home/fregu856/Zenuity/MultiNet/RUNS"
# logdir = os.path.join(runs_dir, default_run)
#
# # Loads the model from rundir
# load_out = load_united_model(logdir)
#
# # Create list of relevant tensors to evaluate
# meta_hypes, subhypes, submodules, decoded_logits, sess, image_pl = load_out
#
# seg_softmax = decoded_logits['segmentation']['softmax']
# eval_list = [seg_softmax]
#
# import utils.train_utils as dec_utils
# print ("Everything MultiNet related is loaded!")
###########################################################################
# MultiNet END:
###########################################################################


# initialize the web server:
app = Flask(__name__)
socketio = SocketIO(app, async_mode = "threading")
# (without "async_mode = "threading", sending stuff to the client (via socketio) doesn't work!)

def web_thread():
    while 1:
        # send all data for display on the web page:
        socketio.emit("new_data", {"throttle_direction": throttle_direction,
                    "steering_direction": steering_direction, "throttle": throttle,
                    "steering_angle": steering_angle, "mode": mode})

        # send a control ping to the RPI (to enable detection of lost wifi connection):
        send_to_RPI("control_ping")

        # delay for 0.1 sec (for ~ 10 Hz loop frequency):
        time.sleep(0.1)

def video_thread():
    global latest_video_frame, latest_video_frame_small
    global latest_video_frame_right, latest_video_frame_small_right
    global latest_video_frame_left, latest_video_frame_small_left
    global steering_direction, throttle_direction

    from datetime import datetime

    # connect to the RPI video stream:
    cap = cv2.VideoCapture("tcp://172.24.1.1:8080")
    # (tcp://<RPI IP address>:<same port number as in start_video_stream.sh>)

    counter = 0
    while True:
        # (this loop will run with the same frequency as the specified camera
        # framerate, which currently is 20 Hz)

        # capture frame-by-frame:
        ret, frame = cap.read()
        latest_video_frame = frame

        # get a smaller version of the frame:
        latest_video_frame_small = cv2.resize(frame, (640, 360))





        # logging of frames and manual steering commands:
        if counter > 40 and len(latest_video_frame_small) > 0 and len(latest_video_frame_small_right) > 0 and len(latest_video_frame_small_left) > 0:
            current_time = str(datetime.now())
            print str(datetime.now())
            cv2.imwrite("log/center_" + current_time + ".png", latest_video_frame_small)
            cv2.imwrite("log/right_" + current_time + ".png", latest_video_frame_small_right)
            cv2.imwrite("log/left_" + current_time + ".png", latest_video_frame_small_left)
            log_file = open("log/log.txt", "a")
            log_file.write("\n")
            log_file.write(current_time + " steering_direction:" + steering_direction
                            + " throttle_direction:" + throttle_direction)
            log_file.close()
            counter = 0
        counter = counter + 1





        # display the resulting frame
        # cv2.imshow("test", latest_video_frame_small_right)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

def video_thread_right():
    global latest_video_frame_right, latest_video_frame_small_right

    from datetime import datetime

    # connect to the RPI video stream:
    cap_right = cv2.VideoCapture("tcp://172.24.1.71:8080")
    # (tcp://<RPI IP address>:<same port number as in start_video_stream.sh>)

    counter = 0
    while True:
        # (this loop will run with the same frequency as the specified camera
        # framerate, which currently is 20 Hz)

        # capture frame-by-frame:
        ret_rigth, frame_right = cap_right.read()
        latest_video_frame_right = frame_right

        # get a smaller version of the frame:
        latest_video_frame_small_right = cv2.resize(frame_right, (640, 360))

        # display the resulting frame
        #cv2.imshow("test", frame)
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break

def video_thread_left():
    global latest_video_frame_left, latest_video_frame_small_left

    from datetime import datetime

    # connect to the RPI video stream:
    cap_left = cv2.VideoCapture("tcp://172.24.1.142:8080")
    # (tcp://<RPI IP address>:<same port number as in start_video_stream.sh>)

    counter = 0
    while True:
        # (this loop will run with the same frequency as the specified camera
        # framerate, which currently is 20 Hz)

        # capture frame-by-frame:
        ret_left, frame_left = cap_left.read()
        latest_video_frame_left = frame_left

        # get a smaller version of the frame:
        latest_video_frame_small_left = cv2.resize(frame_left, (640, 360))

        # display the resulting frame
        #cv2.imshow("test", frame)
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break

def gen_normal():
    while 1:
        if len(latest_video_frame_small_left) > 0: # if we have started receiving actual frames:
            frame = latest_video_frame_small_left

            # convert the latest read video frame to memory buffer format:
            ret, frame_buffer = cv2.imencode(".jpg", frame)

            # get the raw data bytes of 'frame_buffer' (convert to binary):
            frame_bytes = frame_buffer.tobytes()

            # yield ('return') the frame: (yield: returns a value and saves the current
            # state of the generator function. The next time this generator function
            # is called, execution will resume on the next line of code in the function
            # (i.e., it will in this example start a new cycle of the while loop
            # and yield a new frame))
            #
            # what we yield looks like this, but in binary (binary data is a must for multipart):
            # --frame
            # Content-Type: image/jpeg
            #
            # <frame data>
            #
            yield (b'--frame\nContent-Type: image/jpeg\n\n' + frame_bytes + b'\n')

            # delay for 0.05 sec (for ~ 20 Hz loop frequency, we don't get new
            # frames from the camera more frequently than this):
            time.sleep(0.05)

def gen_YOLO():
    while 1:
        if len(latest_video_frame_small) > 0: # if we have started receiving actual frames:
            frame = latest_video_frame_small

            # # compute an appropriate line thickness for the bounding
            # # boxes (depends on the size of the frames):
            # h, w, _ = frame.shape
            # thickness = int((h + w) // 300)
            #
            # # pass the video frame through the tiny-YOLO net:
            # start_YOLO = time.clock()
            # result = tiny_YOLO_net.return_predict(frame)
            # time_YOLO = time.clock() - start_YOLO
            #
            # # draw bounding boxes around all detected objects (and
            # # mark each box with the detected label) on the video frame:
            # for box_data in result:
            #     # get the coordinates of the bounding box:
            #     left = box_data["topleft"]["x"]
            #     top = box_data["topleft"]["y"]
            #     right = box_data["bottomright"]["x"]
            #     bottom = box_data["bottomright"]["y"]
            #     # get the detected class label:
            #     label =  box_data["label"]
            #
            #     # draw the bounding box:
            #     cv2.rectangle(frame, (left, top), (right, bottom), colors[labels.index(label)], thickness)
            #     # mark the bounding box with the class label:
            #     cv2.putText(frame, label, (left, top - 12), 0, 1e-3*h, colors[labels.index(label)], thickness//3)

            # convert the resulting video frame from jpg to memory buffer format:
            ret, frame_buffer = cv2.imencode(".jpg", frame)

            # get the raw data bytes of 'frame_buffer' (convert to binary):
            frame_bytes = frame_buffer.tobytes()

            # yield the frame:
            # what we yield looks like this, but in binary (binary data is a must for multipart):
            # --frame
            # Content-Type: image/jpeg
            #
            # <frame data>
            #
            yield (b'--frame\nContent-Type: image/jpeg\n\n' + frame_bytes + b'\n')

def gen_MultiNet():
    while 1:
        if len(latest_video_frame_small_right) > 0: # if we have started receiving actual frames:
            # Load and reseize Image
            image = latest_video_frame_small_right

            # hypes_road = subhypes['road']
            # image_height = hypes_road['jitter']['image_height']
            # image_width = hypes_road['jitter']['image_width']
            # image = scp.misc.imresize(image, (image_height,
            #                                   image_width, 3),
            #                           interp='cubic')
            #
            # # Run KittiSeg model on image
            # feed_dict = {image_pl: image}
            # output = sess.run(eval_list, feed_dict=feed_dict)
            #
            # seg_softmax = output[0]
            #
            # # Create Segmentation Overlay
            # shape = image.shape
            # seg_softmax = seg_softmax[:, 1].reshape(shape[0], shape[1])
            # hard = seg_softmax > 0.5
            # image = tv_utils.fast_overlay(image, hard)
            #
            # frame = image.astype(np.uint8)
            #
            # print ("New MultiNet output")



            frame = image



            # convert the resulting video frame from jpg to memory buffer format:
            ret, frame_buffer = cv2.imencode(".jpg", frame)

            # get the raw data bytes of 'frame_buffer' (convert to binary):
            frame_bytes = frame_buffer.tobytes()

            # yield the frame:
            # what we yield looks like this, but in binary (binary data is a must for multipart):
            # --frame
            # Content-Type: image/jpeg
            #
            # <frame data>
            #
            yield (b'--frame\nContent-Type: image/jpeg\n\n' + frame_bytes + b'\n')

@app.route("/camera_normal")
def camera_normal():
    # returns a Respone object with a 'gen_normal()' generator function as its data
    # generating iterator. We send a MIME multipart message of subtype Mixed-replace,
    # which means that the browser will read data parts (generated by gen_obj_normal)
    # one by one and immediately replace the previous one and display it. We never
    # close the connection to the client, pretending like we haven't finished sending
    # all the data, and constantly keeps sending new data parts generated by gen_obj_normal.
    #
    # what over time will be sent to the client is the following:
    # Content-Type: multipart/x-mixed-replace; boundary=frame
    #
    # --frame
    # Content-Type: image/jpeg
    #
    #<jpg data>
    #
    # --frame
    # Content-Type: image/jpeg
    #
    #<jpg data>
    #
    # etc, etc
    #
    # where each '--frame' enclosed section represents a jpg image taken from the
    # camera that the browser will read and display one by one, replacing the
    # previous one, thus generating a video stream
    gen_obj_normal = gen_normal()
    return Response(gen_obj_normal, mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route("/camera_YOLO")
def camera_YOLO():
    # return a Respone object with a 'gen_YOLO()' generator function as its
    # data generating iterable, see "camera_normal":
    gen_obj_YOLO = gen_YOLO()
    return Response(gen_obj_YOLO, mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route("/camera_MultiNet")
def camera_MultiNet():
    # return a Respone object with a 'gen_MultiNet()' generator function as its
    # data generating iterable, see "camera_normal":
    gen_obj_MultiNet = gen_MultiNet()
    return Response(gen_obj_MultiNet, mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route("/")
@app.route("/index")
def index():
    try:
        return render_template("index.html")
    except Exception as e:
        return render_template("500.html", error = str(e))

@app.route("/phone")
def phone():
    try:
        return render_template("phone.html")
    except Exception as e:
        return render_template("500.html", error = str(e))

# handle data which is sent from the web page when the user is switching mode (manual or auto):
@socketio.on("mode_event")
def handle_mode_event(sent_dict):
    global mode
    print("Recieved message: " + str(sent_dict["data"]))

    # get the sent mode:
    mode = sent_dict["data"]

    # send the mode to the RPI:
    send_to_RPI(mode)

# handle data which is sent from the web page when the user is manually controlling
# the throttle using WASD (actually, just W and S), and send it to the RPI:
@socketio.on("throttle_arrow_event")
def handle_throttle_arrow_event(sent_dict):
    global throttle_direction
    print("Recieved message: " + str(sent_dict["data"]))

    # get the sent throttle direction:
    throttle_direction = sent_dict["data"]

    # send the throttle direction to the RPI:
    send_to_RPI(throttle_direction)

# handle data which is sent from the web page when the user is manually controlling
# the steering using WASD (actually, just A and D), and send it to the RPI:
@socketio.on("steering_arrow_event")
def handle_steering_arrow_event(sent_dict):
    global steering_direction
    print("Recieved message: " + str(sent_dict["data"]))

    # get the sent steering direction:
    steering_direction = sent_dict["data"]

    # send the steering direction to the RPI:
    send_to_RPI(steering_direction)

@app.errorhandler(404)
def page_not_found(e):
    try:
        return render_template("404.html")
    except Exception as e:
        return render_template("500.html", error = str(e))

if __name__ == '__main__':
    # start a thread constantly reading frames from the RPI video stream:
    thread_video = Thread(target = video_thread)
    thread_video.start()

    thread_video_right = Thread(target = video_thread_right)
    thread_video_right.start()

    thread_video_left = Thread(target = video_thread_left)
    thread_video_left.start()

    # start a thread constantly sending sensor/status data to the web page:
    thread_web = Thread(target = web_thread)
    thread_web.start()

    # start the local web app:
    socketio.run(app, "172.24.1.72")
