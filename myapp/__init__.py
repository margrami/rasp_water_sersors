import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import sys
import datetime
import logging
import io
import config
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from time import sleep
from MCP3008 import MCP3008

app = Flask(__name__)

# database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config.from_object(config)

db = SQLAlchemy(app)
activate_flag = False


from myapp.models import Sensor # noqa
from myapp import routes #noqa
    

db.create_all()
# global variables
adc = MCP3008()
channels = [0, 1, 2, 3, 4, 5]
channels_plant_name = [(0, 'pot1'), (2, 'pot2'), (3, 'Juda_sensor_1'), 
                       (4, 'Juda_sensor_2'), (4, 'Brazito_1'), (5, 'Brazito_2')]






if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')