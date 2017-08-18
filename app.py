from flask import Flask
from flask import render_template
from flask import request
import colorsys
import cv2
import threading
import imutils

#flask init
from flask import Flask
from flask_navigation import Navigation

app = Flask(__name__)
nav = Navigation(app)


#global variables
object_colour = None
colour_lower= None
colour_upper= None
thread1 = threading.Thread()
capture_bool = True



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
    numericalcolour=tuple(int(object_colour[i:i+2], 16) for i in (0, 2 ,4))
    hsv=colorsys.rgb_to_hsv(object_colour[:2],object_colour[2:4],object_colour[4:6])

@app.route('/run', methods=['GET','POST'])
def start_thread():
    #return threading.Thread(target=video_capture())
    return video_capture()


@app.route('/stop', methods=['GET','POST'])
def thread_stop():
    capture_bool = False
    return index()


def video_capture():
    camera = cv2.VideoCapture(0)
    while capture_bool:
        if True:
            pass
        else:
            (grabbed, frame) = camera.read()
            #resize the frame, reduce load on pi, lo
            #lower resolution image/ frame with mean less computation.
            frame = imutils.resize(frame, width=600)

            #convert frame to hsv
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            #create a mask from the users inputted colour
            #this helps detect the object to be tracked
            #with more time edge detection could be used
            #however this is a trade off due to time constraints
            mask =cv2.inRange(hsv,colour_lower,colour_upper)

            #the mask did not origionally get everything
            #use erode to get rid of these artifacts
            mask =	mask = cv2.erode(mask, None, iterations=2)

            #utilising the mask find out where the object is
            contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)[-2]
            obj_center = None

if __name__ == "__main__":
    app.run(host='0.0.0.0',threaded=True)


