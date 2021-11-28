from flask import Flask, render_template, jsonify, Response
import numpy as np
import sys
import datetime
import logging
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from time import sleep
from MCP3008 import MCP3008

app = Flask(__name__)
adc = MCP3008()
channels = [0, 1, 2, 3, 4, 5]
sleepTime = 1

def val(x):
    # function to read the ADC  
    return round(adc.read( channel = x ) /1023.0 *3.3, 2)

def print_interator(it):
    # function to print the values in a interator object (map)
    for x in it:
        print(x, end = '       ')
    print('')


@app.route('/')
def index():
    number = np.random.rand()
    table_data = map(lambda x: val(x), channels)

    return render_template('home.html', x = number, table_data = table_data )


@app.route('/update_decimal', methods=['POST'])
def updatedecimal():
    random_decimal = np.random.rand()
    table_data = map(lambda x: val(x), channels)
    
    return jsonify('', render_template('random_decimal_model.html', x = random_decimal, table_data = table_data))



@app.route ('/plot.png')
def plot_png():
	fig = create_figure()
	output = io.BytesIO()
	FigureCanvas(fig).print_png(output)
	return Response(output.getvalue(), mimetype='image/png')

def create_figure():
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	xs = range(100)
	ys = [random.randint(1, 50) for x in xs]
	axis.plot(xs, ys)
	return fig


if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')