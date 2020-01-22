from shared import db

 
class Sensors(db.Model):
    sensor_db_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    title = db.Column(db.String(80))
    sensor_id = db.Column(db.String())
    sensor_location = db.Column(db.String(80))
    sensor_type = db.Column(db.String(80))
    warning_low = db.Column(db.Integer)
    warning_hi = db.Column(db.Integer)
    alarm_low = db.Column(db.Integer)
    alarm_hi = db.Column(db.Integer)
    mapping_a_reading = db.Column(db.Integer)
    mapping_a_value = db.Column(db.Integer)
    mapping_b_reading = db.Column(db.Integer)
    mapping_b_value = db.Column(db.Integer)
    is_one_wire = db.Column(db.Integer)
    is_analog_sensor = db.Column(db.Integer)



    def __repr__(self):
        return"<Title>: {}>".format(self.title)
    
class SensorLocations(db.Model):
    sensor_location_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    sensor_location_value = db.Column(db.String(80), nullable=False)
    sensor_location_title = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return"<Title>: {}>".format(self.sensor_location_title)

class SensorTypes(db.Model):
    sensor_type_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    sensor_type_value = db.Column(db.String(80), unique=False, nullable=False, primary_key=False)
    sensor_type_title = db.Column(db.String(80), unique=False, nullable=False, primary_key=False)

    def __repr__(self):
        return"<Title>: {}>".format(self.sensor_type_title)


class RPIPins(db.Model):
    rpipins_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    rpipins_type = db.Column(db.String(80))
    rpipins_number = db.Column(db.String(50))
    rpipins_title = db.Column(db.String(80))
    rpipins_clk = db.Column(db.String(2))
    rpipins_cs = db.Column(db.String(2))
    rpipins_miso = db.Column(db.String(2))
    rpipins_mosi = db.Column(db.String(2))

    def __repr__(self):
        return"<Title>: {}>".format(self.rpipins_title)
    

