from flask import Flask
from flask import render_template
from flask import request
import colorsys
import cv2
import threading

app = Flask(__name__)

object_colour = ""
thread1 = threading.Thread()
capture_bool = True
@app.route('/')
def index():
    return render_template('home.jinja2', name="meow")

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


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)



if __name__ == "__main__":
    app.run(host='0.0.0.0',threaded=True)


