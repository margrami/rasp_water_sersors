from flask import Flask, render_template, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
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

# database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///media/pi/exdrive1/rasServer/db/wdb.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
activate_flag = False


class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, nullable=False) 
    plantName = db.Column(db.String(32), nullable=False )
    value = db.Column(db.Float, nullable=False)
    watering = db.Column(db.Boolean)
    wateringML = db.Column(db.Integer)

    def to_dict(self):
        return {
             'id': self.id,
             'number': self.number,
             'time': self.time,
             'value': self.value
        }
    

db.create_all()
# global variables
adc = MCP3008()
channels = [0, 1, 2, 3, 4, 5]
channels_plant_name = [(0, 'pot1'), (2, 'pot2'), (3, 'Juda_sensor_1'), 
                    (4, 'Juda_sensor_2'), (4, 'Brazito_1'), (5, 'Brazito_2')]
sleep_time = 1


def val(x):
    # function to read the ADC  
    return round(adc.read( channel = x ) /1023.0 *3.3, 2)


def print_interator(it):
    # function to print the values in a interator object (map)
    for x in it:
        print(x, end = '       ')
    print('')


def print_dico(dic):
    for k, v in dic.items():
        print(k, v)


def sensor_query(sensorNum):
    return 'SELECT value FROM Sensor WHERE number={0} ORDER BY time'.format(sensorNum)


def sensor_write_db(sensorNum, plantNa):
    dateraw = datetime.datetime.now()
    lecture = Sensor(number=sensorNum, 
                     time=dateraw, 
                     plantName=plantNa, 
                     value=round(val(sensorNum), 1), 
                     watering=False, 
                     wateringML=30)
    db.session.add(lecture)
    x = db.session.commit()
    if x:
        print(x)


def create_figure(sensorNum):
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    print(sensor_query(sensorNum))
    result = db.engine.execute(sensor_query(sensorNum))
    result_as_list = result.fetchall()
    ys = list(result_as_list) # type is class list
    xs = range(result_as_list.__len__()) # type is class range
    axis.set_title('Sensor_{0}'.format(int(sensorNum)-1))
    axis.grid(True)
    axis.set_ylabel('[v]')
    axis.set_xlabel('samples')
    axis.plot(xs, ys)
    return fig


@app.route('/')
def index():
    table_data = map(lambda x: val(x), channels)
    return render_template('home.html', table_data = table_data )


@app.route('/update_decimal', methods=['POST'])
def update_decimal():
    dateraw = datetime.datetime.now()
    lecture_hour = dateraw.strftime("%y-%m-%d_%H:%M:%S")
    table_data = map(lambda x: val(x), channels)
    for index, tuples in enumerate(channels_plant_name):
        x = tuples[0]
        y = tuples[1]
        sensor_write_db(x, y)
    return jsonify('', render_template('random_decimal_model.html', 
                       lecture = lecture_hour, 
                       table_data = table_data))


@app.route('/watering')
def watering():
    return render_template ('home.html', w = 'registrado') 


@app.route('/upgrade')
def upgrade_fig():
    for index, tuples in enumerate(channels_plant_name):
        x = tuples[0]
        y = tuples[1]
        sensor_write_db(x, y)
    return render_template('upgradeFig.html')


@app.route ('/plot1.png')
def plot1_png():
    fig = create_figure(2)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route ('/plot2.png')
def plot2_png():
    fig = create_figure(3)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route ('/plot3.png')
def plot3_png():
    fig = create_figure(4)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route ('/plot4.png')
def plot4_png():
    fig = create_figure(5)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')