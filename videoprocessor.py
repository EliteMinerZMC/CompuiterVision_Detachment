import argparse
from collections import deque

import cv2
import imutils
import numpy as np

(directionX, directionY) = (0, 0)
global counter
counter = 0
global points
direction = ""
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=32,
                help="max buffer size")
args = vars(ap.parse_args())
points = deque(maxlen=args["buffer"])


class VideoCamera(object):
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.video = cv2.VideoCapture(0)
        self.video = cv2.VideoCapture('media/test2.mp4')

        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')

    def __del__(self):
        self.video.release()

    def get_frame(self, mask_colour_lower, mask_colour_upper):
        success, frame = self.video.read()
        origional_image = frame
        direction = ""
        dirX = "No Movment"
        if success == True:
            # camera = cv2.VideoCapture('test.mp4')
            # resize the frame, reduce load on pi, lo
            # lower resolution image/ frame with mean less computation.
            frame = imutils.resize(frame, width=600)

            # convert frame to hsv
            frame = cv2.GaussianBlur(frame, (11, 11), 0)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            # create a mask from the users inputted colour
            # this helps detect the object to be tracked
            # with more time edge detection could be used
            # however this is a trade off due to time constraints

            mask = cv2.inRange(hsv, mask_colour_lower, mask_colour_upper)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            # the mask did not origionally get everything

            # use erode to get rid of these artifacts
            mask = mask = cv2.erode(mask, None, iterations=2)  # utilising the mask find out where the object is
            contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)[-2]
            obj_center = None
            if len(contours) > 0:
                obj_contour = max(contours, key=cv2.contourArea)

                x, y, w, h = cv2.boundingRect(obj_contour)
                M = cv2.moments(obj_contour)
                if M["m00"] != 0:
                    obj_center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                    # where stuff happens - possibly change it to edge detection to draw a bound box
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
                else:
                    obj_center = 0,0

                #make a central dot
                cv2.circle(frame, obj_center, 5, (0, 0, 255), -1)
                global points
                points.appendleft(obj_center)
                plots = np.arange(1, len(points))
                global counter
                counter += 1
                #for each plot check for None, then check for
                for i in plots:
                    if points[i - 1] == None or points[i] == None:
                        # continue skipps following and moves to next iteration of loop
                        ret, jpeg = cv2.imencode('.jpg', origional_image)
                        #return jpeg.tobytes()
                        continue
                    #start detecting print movment - if the object moves in any direction by a degree
                    #it could be considered a failure, however different printers move bed and some just move the bed vertically.
                    #therefore the best way to detect is for left and right movment - given the bed moves frward and backwards
                    if counter >=8 and i==1 and points[-6] is not None:
                        directionX = points[-6][0] - points[i][0]
                        directionY = points[-6][1] - points[i][1]
                        (dirX, dirY) = ("", "")

                        # ensure there is significant movement in the
                        # x-direction movment
                        print (directionX)
                        if np.abs(directionX) > 5:
                            value = np.abs(directionX)
                            dirX = "Movement>5" if np.sign(directionX) == 1 else "Movement>5"

                        if np.abs(directionX) > 10:
                            dirX = "Movement>10"

                        if np.abs(directionX) > 15:
                            dirX = "Movement>15"

                        if np.abs(directionX) > 20:
                            dirX = "Movement>20"

                        if np.abs(directionX) > 30:
                            dirX = "Movement>30"

                        if np.abs(directionX) > 50:
                            dirX = "Movement>50"

                        if np.abs(directionX) > 70:
                            dirX = "Movement>70"

                        else:
                            direction = dirX if dirX != "" else dirY

                        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
                        cv2.line(frame, points[i - 1], points[i], (0, 0, 255), thickness)
                # show the frame to our screen and increment the frame counter
                cv2.putText(frame, dirX, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                            0.65, (0, 0, 255), 3)
                ret, jpeg = cv2.imencode('.jpg', frame)
                return jpeg.tobytes()
