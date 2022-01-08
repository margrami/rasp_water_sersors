import os
from MCP3008 import MCP3008
from myapp import app, db
from myapp.models import Sensor, Messures
import logging
import io
import datetime
from time import sleep
import RPi.GPIO as GPIO


secondsinterval = 30
adc = MCP3008()
init = False
GPIO.setmode(GPIO.BCM) # use BCM numbering pin numbers


def populate_main_struct():
    # {'data': [{'number': 2, 'plantName': 'brazito_1', 'motor_number': 1}, 
    # {'number': 3, 'plantName': 'brazito_2', 'motor_number': 2}, {'number': 4, 'plantName': 'juda_1', 'motor_number': 4}, 
    # {'number': 5, 'plantName': 'juda_2', 'motor_number': 3}]}
    return {'data':[sensor.to_dict() for sensor in Sensor.query]}


def val(x):
    # function to read the ADC  
    return round(adc.read( channel = x ) /1023.0 *3.3, 2)


def sensor_write_db(sensorNum:int, plantNa:str):
	# Populate the table Messures
    dateraw = datetime.datetime.now()
    lecture = Messures(sensor_id=sensorNum, 
                       time=dateraw,
                       value=round(val(sensorNum), 1))
    db.session.add(lecture)
    db.session.commit()


def init_output(pin):
    # motor function, to setup the motor's pins as output 
    GPIO.setup(pin, GPIO.OUT) # set up channel as an output.
    GPIO.output(pin, GPIO.HIGH) # set the motor in 1 because it is inversed logic


def manual_pump(pump_pin:int, delay:int):
    init_output(pump_pin)
    GPIO.output(pump_pin, GPIO.LOW)
    sleep(delay)
    GPIO.output(pump_pin, GPIO.HIGH)



for i in range(4500):
    structure = populate_main_struct()
    for item in structure['data']:
        # db write lecture
        sensor_write_db(item['number'], item['plantName'])
        # eval sensor_value to power pumps
        sensor_value = val(item['number'])
        print(item['number'], sensor_value, item['motor_GPIO_pin'])
        if sensor_value > 2:
            print(item['number'], sensor_value, 'activo motor en :', item['motor_GPIO_pin'])
            manual_pump(pump_pin=item['motor_GPIO_pin'], delay=2)
    sleep(secondsinterval)

#if __name__ == "__main__":
#	main()