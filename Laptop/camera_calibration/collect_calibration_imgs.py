import numpy as np
import cv2

# connect to the RPI video stream:
cap = cv2.VideoCapture("tcp://172.24.1.1:8080")

counter = 1
img_counter = 1
while True:
    # read the latest frame from the video stream:
    ret, frame = cap.read()

    # display the resulting frame
    cv2.imshow("test", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # save an image to disk with a frequency of ~ 1 Hz:
    if counter > 20: # (frames are read with 20 Hz)
        cv2.imwrite("img_" + str(img_counter) + ".png", frame)
        img_counter += 1
        counter = 0

    counter +=1

# when everything is done, release the capture and close the img window:
cap.release()
cv2.destroyAllWindows()
