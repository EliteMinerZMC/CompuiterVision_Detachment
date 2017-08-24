import logging
import os
from builtins import len
from flask import Flask
from flask import request, render_template, Response
import colorsys
import cv2
import threading
import imutils
from collections import deque
import argparse
# flask init
from flask import Flask
from flask_navigation import Navigation
from videoprocessor import VideoCamera
import numpy as np
from PIL import Image

app = Flask(__name__)
nav = Navigation(app)
UPLOAD_FOLDER = '\\media\\images\\'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
global temp_colour
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
    return render_template('settings.jinja2')


@app.route('/fileupload', methods=['POST'])
def extra():
    #after running the initial settings page
    #where user uploads filament colour
    #return to main page
    image = request.files['file']
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    path =APP_ROOT + app.config['UPLOAD_FOLDER']
    image.save(os.path.join(path, 'filament.png'))
    image = cv2.imread('media/images/filament.png')
    avg_color_per_row = np.average(image, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    global hsv_colour
    hsv_colour = avg_color
    hsv_colour = colorsys.rgb_to_hsv(hsv_colour[0] / 255, hsv_colour[1] / 255, hsv_colour[2] / 255)
    h = hsv_colour[0] * 120
    s = hsv_colour[1] * 120
    v = hsv_colour[2] * 120
    hsv_colour = (h, s, v)
    return render_template('home.jinja2')

#this now works, file upload works, now to get colour from image


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
    return ""


@app.route('/stop', methods=['GET', 'POST'])
def thread_stop():
    capture_bool = False
    return index()


def get_colours_lower(colour):
    s=50
    v=50
    colour_lower = (colour[0], s, v)
    if colour[0]>=10:
        colour_lower = ((colour[0] - 10), s, v)
    return colour_lower


def get_colours_upper(colour):
    colour_upper = (colour[0], 255, 255)
    if colour[0]<=179:
        colour_upper = ((colour[0] + 160), 255, 255)
    return colour_upper


def gen(camera):
    while True:
        frame = camera.get_frame(get_colours_lower(hsv_colour), get_colours_upper(hsv_colour))
        if frame == None:
            continue
        else:
            yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)
