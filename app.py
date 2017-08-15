from flask import Flask
from flask import render_template
from flask import request
import colorsys


app = Flask(__name__)

object_colour = ""

@app.route('/')
def index():
    return render_template('home.jinja2', name="meow")

@app.route('/', methods=['GET', 'POST'])
def parse_request():
    colour = request.form['colour']  # data is empty
    object_colour = colour.lstrip('#')
    numericalcolour=tuple(int(object_colour[i:i+2], 16) for i in (0, 2 ,4))
    hsv=colorsys.rgb_to_hsv(object_colour[:2],object_colour[2:4],object_colour[4:6])
    print_colour = hsv
    # need posted data here

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)



if __name__ == "__main__":
    app.run(host='0.0.0.0')


