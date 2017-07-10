# NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE!
# This code is NOT used, it's just saved for future reference
# NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE! NOTE!

from darkflow.net.build import TFNet
import cv2
import numpy as np

def _to_color(indx, base):
    """ return (b, r, g) tuple"""
    base2 = base * base
    b = 2 - indx / base2
    r = 2 - (indx % base2) / base
    g = 2 - (indx % base2) % base
    return (b * 127, r * 127, g * 127)

labels = ["aeroplane", "bicycle", "bird", "boat", "bottle",
    "bus", "car", "cat", "chair", "cow", "diningtable", "dog",
    "horse", "motorbike", "person", "pottedplant", "sheep", "sofa",
    "train", "tvmonitor"]

colors = list()
base = int(np.ceil(pow(len(labels), 1./3)))
for x in range(len(labels)):
	colors += [_to_color(x, base)]



options = {"model": "/home/fregu856/darkflow/cfg/tiny-yolo-voc.cfg",
            "load": "/home/fregu856/darkflow/bin/tiny-yolo-voc.weights",
            "threshold": 0.2}
tfnet = TFNet(options)

print "Everything loaded"

imgcv = cv2.imread("/home/fregu856/darkflow/sample_img/attention_1.png")

h, w, _ = imgcv.shape
thick = int((h + w) // 300)

result = tfnet.return_predict(imgcv)

for box_data in result:
    left = box_data["topleft"]["x"]
    top = box_data["topleft"]["y"]

    right = box_data["bottomright"]["x"]
    bottom = box_data["bottomright"]["y"]

    mess =  box_data["label"]

    cv2.rectangle(imgcv, (left, top), (right, bottom), colors[labels.index(mess)], thick)
    cv2.putText(imgcv, mess, (left, top - 12), 0, 1e-3*h, colors[labels.index(mess)], thick//3)

cv2.imshow("test_img", imgcv)
cv2.waitKey(0)
