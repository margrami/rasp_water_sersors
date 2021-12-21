import os
from MCP3008 import MCP3008
from myapp import app, db
from myapp.models import Sensor, Messures
import logging
import io
import datetime
from time import sleep


secondsinterval = 60
adc = MCP3008()
channels = [0, 1, 2, 3, 4, 5]
channels_plant_name = [(0, 'pot1'), (1, 'pot2'), (2, ''), 
                       (3, ''), (4, ''), (5, ''), (6, 'N/A'), (7, 'N/A')]


def val(x):
    # function to read the ADC  
    return round(adc.read( channel = x ) /1023.0 *3.3, 2)


def sensor_config_query(sensorNum:int):
    return 'SELECT plantName FROM Sensor WHERE number={0}'.format(sensorNum)


def sensor_write_db(sensorNum:int, plantNa:str):
	# Populate the table Messures
    dateraw = datetime.datetime.now()
    lecture = Messures(sensor_id=sensorNum, 
                       time=dateraw,
                       value=round(val(sensorNum), 1))
    db.session.add(lecture)
    db.session.commit()


def confirm_config():
    """
    Populate the structure channels_plant_name: list of tuples from info in db
    The db_session.execute(query) returns a ResultProxy object
    The ResultProxy object is made up of RowProxy objects
    The RowProxy object has an .items() method that returns key, value tuples 
    of all the items in the row, which can be unpacked as key, value in a for operation.
    [{column: value for column, value in _row.items()} for _row in y]
    """

    for i in range(2,8):
        y = db.engine.execute(sensor_config_query(i))
        for _row in y:
            for column, value in _row.items():
                channels_plant_name[int(i)] = (i, str(value))


for i in range(4500):
    dateraw = datetime.datetime.now()
    lecture_hour = dateraw.strftime("%y-%m-%d_%H:%M:%S")
    confirm_config()
    for index, tuples in enumerate(channels_plant_name):
        x = tuples[0]
        y = tuples[1]
        sensor_write_db(x, y)
    sleep(secondsinterval)

#if __name__ == "__main__":
#	main()