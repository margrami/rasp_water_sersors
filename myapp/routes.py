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
init = False
GPIO.setmode(GPIO.BCM) # use BCM numbering pin numbers
sampling_time = 30

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


def sensor_write_db_x(sensorNum:int, plantNa:str, motorNum:int, motorGPIOpin:int):
    # to be used the 1st time, otherwise the update doesn't work
    lecture = Sensor(number=sensorNum, 
                     plantName=plantNa,
                     motor_number=motorNum,
                     motor_GPIO_pin=motorGPIOpin)
    db.session.add(lecture)
    db.session.commit()


def sensor_write_db(sensorNum:int, plantNa:str, motorNum:int, motorGPIOpin:int):
    # this is the procedure to update in sqlalchemy
    # use to upgrate the Sensor.plantName - to updating Don't forget the dict
    rows_changed = Sensor.query.filter_by(number=sensorNum).update(dict(plantName=str(plantNa), 
                                                                        motor_number=motorNum,
                                                                        motor_GPIO_pin=motorGPIOpin))
    db.session.commit()


def sensor_config_query(sensorNum:str):
    # this is just the query text. Must be uses with the db.engine.execute command.
    return 'SELECT plantName FROM Sensor WHERE number={0}'.format(sensorNum)


def messure_query_1day_ago(sensorNum:str):
    # this is just the query's text. Must be uses with the db.engine.execute command.
    return 'SELECT value FROM Messures WHERE sensor_id={0} AND time >= date("now","-1 day") ORDER BY time'.format(sensorNum)


def populate_main_struct():
    # Extract configuration on DB and populate the structure:  
    # {'data': [{'number': 2, 'plantName': 'brazito_1', 'motor_number': 1}, 
    # {'number': 3, 'plantName': 'brazito_2', 'motor_number': 2}, {'number': 4, 'plantName': 'juda_1', 'motor_number': 4}, 
    # {'number': 5, 'plantName': 'juda_2', 'motor_number': 3}]}
    return {'data':[sensor.to_dict() for sensor in Sensor.query]}


def create_figure(sensorNum:int):
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    #result = db.engine.execute(messure_query(sensorNum))
    result = db.engine.execute(messure_query_1day_ago(sensorNum))
    result_as_list = result.fetchall()
    ys = list(result_as_list) # type is class list
    xs = range(result_as_list.__len__()) # type is class range
    _plant_name = [item['plantName'] for item in global_struture['data'] if item['number']== sensorNum]
    axis.set_title('Sensor_{0} {1}'.format(int(sensorNum)-1, _plant_name)) # replace this
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
    init_output(pin=pump_pin)
    GPIO.output(pump_pin, GPIO.LOW)


# global variables
global_struture = populate_main_struct()


@app.route('/')
def index():
    #confirm_config()
    print({'data': [sensor.to_dict() for sensor in Sensor.query]})
    table_data = map(lambda x: val(x), channels)
    return render_template('home.html', table_data = table_data,
                                        new_sampling=sampling_time,
                                        sensor_table={'data': [sensor.to_dict() for sensor in Sensor.query]})


@app.route('/update_decimal', methods=['POST'])
def update_decimal():
    dateraw = datetime.datetime.now()
    lecture_hour = dateraw.strftime("%y-%m-%d_%H:%M:%S")
    table_data = map(lambda x: val(x), channels)
    return jsonify('', render_template('random_decimal_model.html', 
                       lecture = lecture_hour, 
                       table_data = table_data))

@app.route('/setupsetupspgtime', methods=['POST'])
def setup_sampling_time():
    sampling_time = request.form.get("samptime")
    return render_template('home.html', 
                            new_sampling=sampling_time,
                            sensor_table={'data': [sensor.to_dict() for sensor in Sensor.query]})


@app.route('/config', methods=["POST"])
def configuration():
    try:
        x = request.form.get("sen_name")
        y = request.form.get("plant_name")
        z = request.form.get("motor_name")
        w = request.form.get("GPIO_pin")
        sensor_write_db(sensorNum=x, plantNa=y, motorNum=z, motorGPIOpin=w)
        return render_template ('home.html', w = 'registrado',
                                             new_sampling=sampling_time,
                                             sensor_table={'data': [sensor.to_dict() for sensor in Sensor.query]})
    except:
        message = 'Selecione un sensor!'
        return render_template ('error.html', message = message,
                                              new_sampling=sampling_time,
                                              sensor_table={'data': [sensor.to_dict() for sensor in Sensor.query]})


@app.route('/activate_motor/<int:motor_num>')
def activate_motor(motor_num):
    my_text ='Activating Motor {0}'.format(str(motor_num))
    print(my_text, motor_num)
    manual_pump(pump_pin=motor_num, delay=1)
    return my_text


@app.route('/stop_motor/<int:motor_num>')
def stop_motor(motor_num):
    my_text ='Stopping Motor {0} '.format(str(motor_num))
    init_output(pin=motor_num)
    print(my_text, motor_num)
    return my_text


@app.route ('/plot1.png')
def plot1_png():
    fig = create_figure(sensorNum=2)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route ('/plot2.png')
def plot2_png():
    fig = create_figure(sensorNum=3)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route ('/plot3.png')
def plot3_png():
    fig = create_figure(sensorNum=4)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route ('/plot4.png')
def plot4_png():
    fig = create_figure(sensorNum=5)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route('/samplingtime')
def samplingtime():
    return jsonify({'new_sampling':sampling_time})


