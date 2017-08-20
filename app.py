import logging
from builtins import len
from flask import Flask
from flask import request, render_template, Response
import colorsys
import cv2
import threading
import imutils
from collections import deque
import numpy as np
import argparse
# flask init
from flask import Flask
from flask_navigation import Navigation
from videoprocessor import VideoCamera

app = Flask(__name__)
nav = Navigation(app)

# global variables
global object_colour
global colour_lower
global colour_upper
thread1 = threading.Thread()
capture_bool = True
counter = 0
(dX, dY) = (0, 0)
direction = ""
global hsv_colour
hsv_colour = ""
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=32,
                help="max buffer size")
args = vars(ap.parse_args())
points = deque(maxlen=args["buffer"])




nav.Bar('top', [
    nav.Item('Home', 'index'),
    nav.Item('Extras', 'extra'),
])


@app.route('/')
def index():
    return render_template('home.jinja2')


@app.route('/extra')
def extra():
    return render_template('hello.html')


@app.route('/', methods=['GET', 'POST'])
def parse_request():
    colour = request.form['colour']  # data is empty
    object_colour = colour.lstrip('#')

    numericalcolour = tuple(int(object_colour[i:i + 2], 16) for i in (0, 2, 4))
    global hsv_colour
    hsv_colour = colorsys.rgb_to_hsv(numericalcolour[0] / 255, numericalcolour[1] / 255, numericalcolour[2] / 255)
    h = hsv_colour[0] * 120
    s = hsv_colour[1] * 120
    v = hsv_colour[2] * 120
    hsv_colour = (h, s, v)
    return index()


@app.route('/run', methods=['GET', 'POST'])
def start_thread():
    # return threading.Thread(target=video_capture())
    return video_capture()


@app.route('/stop', methods=['GET', 'POST'])
def thread_stop():
    capture_bool = False
    return index()


def get_colours_lower(colour):
    colour_lower = ((colour[0] - 50), (colour[1] - 30), 25)
    return colour_lower


def get_colours_upper(colour):
    colour_upper = ((colour[0] + 30), 255, 255)
    return colour_upper


def video_capture():
    # camera = cv2.VideoCapture(0)
    camera = cv2.VideoCapture('test.mp4')
    while capture_bool:
        (grabbed, frame) = camera.read()
        # resize the frame, reduce load on pi, lo
        # lower resolution image/ frame with mean less computation.
        frame = imutils.resize(frame, width=600)

        # convert frame to hsv
        frame = imutils.resize(frame, width=600)
        frame = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # create a mask from the users inputted colour
        # this helps detect the object to be tracked
        # with more time edge detection could be used
        # however this is a trade off due to time constraints
        mask_colour_lower = get_colours_lower(hsv_colour)
        mask_colour_upper = get_colours_upper(hsv_colour)
        mask = cv2.inRange(hsv, mask_colour_lower, mask_colour_upper)
        #cv2.imshow("mask", hsv)
        #cv2.waitKey()
        #cv2.imshow("mask",mask)
        #cv2.waitKey()
        # the mask did not origionally get everything
        # use erode to get rid of these artifacts
        mask = mask = cv2.erode(mask, None, iterations=2)
        # utilising the mask find out where the object is
        contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)[-2]
        obj_center = None
        logging.debug("Shown","","")
        if len(contours) > 0:
            obj_contour = max(contours, key=cv2.contourArea)

            x, y, w, h = cv2.boundingRect(obj_contour)
            M = cv2.moments(obj_contour)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            # where stuff happens - possibly change it to edge detection to draw a bound box
            cv2.rectangle(frame, (x,y), (x+w,y+h), (0, 255, 255), 2)
            # cv2.circle(frame, (int(x), int(y)), int(radius),
            #           (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            points.appendleft(center)

            for i in np.arange(1, len(points)):
                if points[i - 1] == None or points[i] == None:
                    # continue skipps following and moves to next iteration of loop
                    continue

                # show the frame to our screen and increment the frame counter
                ret, jpeg = cv2.imencode('.jpg', frame)
                #cv2.imshow("meow",frame)
                #cv2.waitKey()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)
