import os
from MCP3008 import MCP3008
from myapp import app, db
from myapp.models import Sensor
import logging
import io
import datetime
from time import sleep


secondsinterval = 10
adc = MCP3008()
channels = [0, 1, 2, 3, 4, 5]
channels_plant_name = [(0, 'pot1'), (2, 'pot2'), (3, 'Juda_sensor_1'), 
                       (4, 'Juda_sensor_2'), (4, 'Brazito_1'), (5, 'Brazito_2')]



def val(x):
    # function to read the ADC  
    return round(adc.read( channel = x ) /1023.0 *3.3, 2)


def sensor_write_db(sensorNum, plantNa):
    dateraw = datetime.datetime.now()
    lecture = Sensor(number=sensorNum, 
                     time=dateraw, 
                     plantName=plantNa, 
                     value=round(val(sensorNum), 1), 
                     watering=False, 
                     wateringML=30)
    db.session.add(lecture)
    db.session.commit()


for i in range(10):
    dateraw = datetime.datetime.now()
    lecture_hour = dateraw.strftime("%y-%m-%d_%H:%M:%S")
    for index, tuples in enumerate(channels_plant_name):
        x = tuples[0]
        y = tuples[1]
        sensor_write_db(x, y)
        sleep(secondsinterval)
print('Done!')

if __name__ == "__main__":
	main()