from myapp import db

class Sensor(db.Model):
    __tablename__ = "Sensor"
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    plantName = db.Column(db.String(32), nullable=False)
    motor_number = db.Column(db.Integer, nullable=False)
    motor_GPIO_pin = db.Column(db.Integer, nullable= False)

    def to_dict(self):
        return {
             'number': self.number,
             'plantName': self.plantName,
             'motor_number': self.motor_number,
             'motor_GPIO_pin': self.motor_GPIO_pin
        }


class Messures(db.Model):
    __tablename__ = "Messures"
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("Sensor.number"), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    value = db.Column(db.Float, nullable=False)


# class Motors(db.Model):
#     __tablename__ = "Motor"
#     id = db.Column(db.Integer, primary_key=True)
#     number = db.Column(db.Integer, nullable= False)
#     sensor_linked = db.Column(db.Integer, db.ForeignKey("Sensor.number"), nullable=False)
#     activ_time = db.Column(db.DateTime)
#     GPIO_pin = db.Column(db.Integer, nullable= False)

#     def to_dict(self):
#         return {
#              'number': self.number,
#              'sensor_linked': self.sensor_linked,
#              'GPIO_pin': self.GPIO_pin,
#              'activ_time': self.activ_time
#         }


