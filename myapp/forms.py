from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField, TextField, IntegerField

class SensorForm(FlaskForm):
    sensor_number = IntegerField('Sensor #', NumberRange(1, 8))
    plant_name = StringField('Plant Name')
    submit = SubmitField('Configure')