from myapp import app, db
from myapp.models import Sensor
from flask import render_template, jsonify, Response, request
from MCP3008 import MCP3008
import RPi.GPIO as GPIO
import numpy as np
import sys
import datetime
import config
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
from time import sleep


# global variables
adc = MCP3008()
channels = [0, 1, 2, 3, 4, 5]
channels_plant_name = [(0, 'pot1'), (1, 'pot2'), (2, ''), 
                       (3, ''), (4, ''), (5, ''), (6, 'N/A'), (7, 'N/A')]

init = False
GPIO.setmode(GPIO.BCM) # use BCM numbering pin numbers

# ------------------

def val(x:int):
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


def print_tuples_list(it):
    for (x,y) in it:
        print(x , y)


def messure_query(sensorNum:int):
    return 'SELECT value FROM Messures WHERE sensor_id={0} ORDER BY time'.format(sensorNum)


def sensor_write_db_x(sensorNum:int, plantNa:str):
    # to be used the 1st time, otherwise the update doesn't work
    lecture = Sensor(number=sensorNum, 
                     plantName=plantNa)
    db.session.add(lecture)
    db.session.commit()


def sensor_write_db(sensorNum:int, plantNa:str):
    # this is the procedure to update in sqlalchemy
    # use to upgrate the Sensor.plantName - to updating Don't forget the dict
    rows_changed = Sensor.query.filter_by(number=sensorNum).update(dict(plantName=str(plantNa)))
    db.session.commit()

def sensor_config_query(sensorNum:str):
    # this is just the query text. Must be uses with the db.engine.execute command.
    return 'SELECT plantName FROM Sensor WHERE number={0}'.format(sensorNum)


def messure_query_1day_ago(sensorNum:str):
    # this is just the query's text. Must be uses with the db.engine.execute command.
    return 'SELECT value FROM Messures WHERE sensor_id={0} AND time >= date("now","-1 day") ORDER BY time'.format(sensorNum)


def confirm_config():
    """
    Populate the structure channels_plant_name: list of tuples from info in Sensor db 
    The db_session.execute(query) returns a ResultProxy object
    The ResultProxy object is made up of RowProxy objects
    The RowProxy object has an .items() method that returns key, value tuples 
    of all the items in the row, which can be unpacked as key, value in a for operation.
    [{column: value for column, value in rowproxy.items()} for rowproxy in resultproxy]
    """

    for i in range(2,8):
        y = db.engine.execute(sensor_config_query(i))
        for _row in y:
            for column, value in _row.items():
                channels_plant_name[int(i)] = (i, str(value))


def create_figure(sensorNum:int):
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    #result = db.engine.execute(messure_query(sensorNum))
    result = db.engine.execute(messure_query_1day_ago(sensorNum))
    result_as_list = result.fetchall()
    ys = list(result_as_list) # type is class list
    xs = range(result_as_list.__len__()) # type is class range
    _tuple = channels_plant_name[sensorNum]
    axis.set_title('Sensor_{0} {1}'.format(int(sensorNum)-1, _tuple[1])) # replace this
    axis.grid(True)
    axis.set_ylabel('[v]')
    axis.set_xlabel('samples')
    axis.plot(xs, ys)
    print('en create_figure')
    return fig


def init_output(pin):
    # motor function, to setup the motor's pins as output 
    GPIO.setup(pin, GPIO.OUT) # set up channel as an output.
    GPIO.output(pin, GPIO.HIGH) # set the motor in 1 because it is inversed logic


def manual_pump(pump_pin:int, delay:int):
    init_output(pump_pin)
    GPIO.output(pump_pin, GPIO.LOW)
    #sleep(1)
    #GPIO.output(pump_pin, GPIO.HIGH)
    #sleep(1)


@app.route('/')
def index():
    confirm_config()
    print([sensor.to_dict() for sensor in Sensor.query])
    table_data = map(lambda x: val(x), channels)
    return render_template('home.html', table_data = table_data, 
                                        sensor_table=channels_plant_name,
                                        parent_list=[sensor.to_dict() for sensor in Sensor.query])


@app.route('/update_decimal', methods=['POST'])
def update_decimal():
    dateraw = datetime.datetime.now()
    lecture_hour = dateraw.strftime("%y-%m-%d_%H:%M:%S")
    table_data = map(lambda x: val(x), channels)
    return jsonify('', render_template('random_decimal_model.html', 
                       lecture = lecture_hour, 
                       table_data = table_data))



@app.route('/config', methods=["POST"])
def configuration():
    try:
        x = request.form.get("sen_name")
        y = request.form.get("plant_name")
        channels_plant_name[int(x)] = (int(x), str(y))
        sensor_write_db(x, y)

        return render_template ('home.html', w = 'registrado', 
                                             sensor_table=channels_plant_name)
    except:
        message = 'Selecione un sensor!'
        return render_template ('error.html', message = message, 
                                              sensor_table=channels_plant_name )


@app.route('/upgrade')
def upgrade_fig():
    for index, tuples in enumerate(channels_plant_name):
        x = tuples[0]
        y = tuples[1]
        sensor_write_db(x, y)
    return render_template('upgradeFig.html')


@app.route('/activate_motor/<int:motor_num>')
def activate_motor(motor_num):
    my_text ='Activating Motor {0}'.format(str(motor_num))
    print(my_text, motor_num)
    manual_pump(motor_num, 1)
    return my_text


@app.route('/stop_motor/<int:motor_num>')
def stop_motor(motor_num):
    my_text ='Stopping Motor {0} '.format(str(motor_num))
    init_output(motor_num)
    print(my_text, motor_num)
    return my_text


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


