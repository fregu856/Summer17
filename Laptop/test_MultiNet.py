# NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE!
# This code is NOT used, it's just saved for future reference
# NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE!

# This code is a modified version of demo.py in https://github.com/MarvinTeichmann/MultiNet

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import json
import logging
import os
import sys
import collections
import cv2
import numpy as np
import scipy as scp
import scipy.misc
import tensorflow as tf
import time
from PIL import Image, ImageDraw, ImageFont

# add the "TensorVision" dir to the path so that its content can be imported:
import sys
sys.path.append("/home/fregu856/Zenuity/MultiNet/submodules/TensorVision")
import tensorvision.utils as tv_utils
import tensorvision.core as core

default_run = 'MultiNet_ICCV'
weights_url = ("ftp://mi.eng.cam.ac.uk/"
               "pub/mttt2/models/MultiNet_ICCV.zip")

def load_united_model(logdir):
    subhypes = {}
    subgraph = {}
    submodules = {}
    subqueues = {}

    first_iter = True

    meta_hypes = tv_utils.load_hypes_from_logdir(logdir, subdir="",
                                                 base_path='hypes')
    for model in meta_hypes['models']:
        subhypes[model] = tv_utils.load_hypes_from_logdir(logdir, subdir=model)
        hypes = subhypes[model]
        hypes['dirs']['output_dir'] = meta_hypes['dirs']['output_dir']
        hypes['dirs']['image_dir'] = meta_hypes['dirs']['image_dir']
        submodules[model] = tv_utils.load_modules_from_logdir(logdir,
                                                              dirname=model,
                                                              postfix=model)

        modules = submodules[model]

    image_pl = tf.placeholder(tf.float32)
    image = tf.expand_dims(image_pl, 0)
    image.set_shape([1, 384, 1248, 3])
    decoded_logits = {}

    for model in meta_hypes['models']:
        hypes = subhypes[model]
        modules = submodules[model]
        optimizer = modules['solver']

        with tf.name_scope('Validation_%s' % model):
            reuse = {True: False, False: True}[first_iter]

            scope = tf.get_variable_scope()

            with tf.variable_scope(scope, reuse=reuse):
                logits = modules['arch'].inference(hypes, image, train=False)

            decoded_logits[model] = modules['objective'].decoder(hypes, logits,
                                                                 train=False)

        first_iter = False

    sess = tf.Session()
    saver = tf.train.Saver()
    cur_step = core.load_weights(logdir, sess, saver)

    return meta_hypes, subhypes, submodules, decoded_logits, sess, image_pl


tv_utils.set_gpus_to_use()

runs_dir = "/home/fregu856/Zenuity/MultiNet/RUNS"
logdir = os.path.join(runs_dir, default_run)

# Loads the model from rundir
load_out = load_united_model(logdir)

# Create list of relevant tensors to evaluate
meta_hypes, subhypes, submodules, decoded_logits, sess, image_pl = load_out

seg_softmax = decoded_logits['segmentation']['softmax']
eval_list = [seg_softmax]

import utils.train_utils as dec_utils

for i in range(2):
    # Load and reseize Image
    image_file = "/home/fregu856/Zenuity/MultiNet/data/demo/test%d.jpg" % i
    image = scp.misc.imread(image_file)

    hypes_road = subhypes['road']
    image_height = hypes_road['jitter']['image_height']
    image_width = hypes_road['jitter']['image_width']
    image = scp.misc.imresize(image, (image_height,
                                      image_width, 3),
                              interp='cubic')

    # Run KittiSeg model on image
    feed_dict = {image_pl: image}
    output = sess.run(eval_list, feed_dict=feed_dict)

    seg_softmax = output[0]

    # Create Segmentation Overlay
    shape = image.shape
    seg_softmax = seg_softmax[:, 1].reshape(shape[0], shape[1])
    hard = seg_softmax > 0.5
    image = tv_utils.fast_overlay(image, hard)

    image = image.astype(np.uint8)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    cv2.imshow("test", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
