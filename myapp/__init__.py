import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from flask_bootstrap import Bootstrap



app = Flask(__name__)
# database
#basedir = os.path.abspath(os.path.dirname(__file__))
app.config.from_object('config')
db = SQLAlchemy(app)
activate_flag = False


from myapp.models import Sensor # noqa


db.create_all()
from myapp import routes #noqa



if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')