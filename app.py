import os
from flask import Flask, render_template, request



from sqlalchemy import event, DDL


project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir,"yachtbraindatabase.db"))


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

from shared import db
db.init_app(app)
 
#import our data models
from models import Sensors, SensorLocations, SensorTypes

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/create_database')
def create_database():
    from database_create import insert_initial_values_sensor_locations, insert_initial_values_sensor_types
    print('pre listen')
    #event.listen(SensorLocations.__table__, 'after_create', insert_initial_values_sensor_locations)
    #event.listen(SensorTypes.__table__, 'after_create', insert_initial_values_sensor_types)
 
    print('pre create')
    db.create_all()
    print('post create')

    insert_initial_values_sensor_locations()
    insert_initial_values_sensor_types()
    print('post values')
    return render_template("index.html")

@app.route('/sensors', methods=["GET", "POST"])
def sensors():

    #if a form is posted we add the data
    if request.form:
        sensor_db_id = request.form.get("sensor_db_id")

        sensor = Sensors(title = request.form.get("title")
        , sensor_id = request.form.get("sensor_id")
        , sensor_location = request.form.get("sensor_location")
        , sensor_type = request.form.get("sensor_type")
        , warning_low = request.form.get("warning_low")
        , warning_hi = request.form.get("warning_hi")
        , alarm_low = request.form.get("alarm_low")
        , alarm_hi = request.form.get("alarm_hi")
        , mapping_a_reading = request.form.get("mapping_a_reading")
        , mapping_a_value = request.form.get("mapping_a_value")
        , mapping_b_reading = request.form.get("mapping_b_reading")
        , mapping_b_value = request.form.get("mapping_b_value")
        , is_one_wire = request.form.get("is_one_wire")
        , is_analog_sensor = request.form.get("is_analog_sensor"))
        
        # if this sensor already exists in the db we update
        if sensor_db_id:
            #update record
            
            sensor.sensor_db_id = sensor_db_id
            db.session.merge(sensor)
            db.session.commit()
            
        else:
            #insert record   
            db.session.add(sensor)
            db.session.commit()
        

    #here we have the normal behavior of the page
    #get all the sensors in database
    #get all sensors on the bus
    #compare the list of each against each other, place the non-assigned sensors at the top of the page maybe?
     
    #get all the possible sensor locations
    sensor_locations = SensorLocations.query.order_by(SensorLocations.sensor_location_value).all()
    #get all the possible sensor types
    sensor_types = SensorTypes.query.order_by(SensorTypes.sensor_type_value).all()
    
    from lib import OneWireSensors

    #get all sensors off the onewire bus
    sensor_ids_onewire = OneWireSensors.get_all_onewire_ids()

    #get all sensors stored in the database
    sensors = Sensors.query.order_by(Sensors.title).all()

    #loop through all sensors saved in db and create an array of the sensor id's
    sensors_in_database = []
    for sensor in sensors:
        sensors_in_database.append(sensor.sensor_id)

    

    for sensor_id in sensor_ids_onewire:
        if sensor_id not in sensors_in_database:
            print('not in array')
            #sensors.update({'sensor_id':sensor_id})
            #sensors[sensor_id] = []
            #sensors[sensor_id]['sensor_id'] = sensor_id
            
    print(sensors)

    
    return render_template("sensors.html", sensors = sensors, sensor_locations=sensor_locations,sensor_types=sensor_types)



      

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
