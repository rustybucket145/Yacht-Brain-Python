import os
from flask import Flask, render_template, request

print('top of script')

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
    print('starting index')
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
    print('starting sensors')
   
    print('starting SensorsQuery')
    #get all sensors stored in the database
    sensors = Sensors.query.order_by(Sensors.title).all()
    
    print('starting loop through sensors in DB to build array')
    #loop through all sensors saved in db and create an array of the sensor id's
    sensors_in_database = []
    for sensor in sensors:
        sensors_in_database.append(sensor.sensor_id)
    
    #if a form is posted we add the data
    if request.form:
        print('form was posted')
        sensor_db_id = request.form.get("sensor_db_id")

        # its adding a new one on update... change to do an update        
        sensor = Sensors(title = request.form.get("title")
        , sensor_db_id = request.form.get("sensor_db_id")
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
        if sensor_db_id is not '':
            #update record
            print('form is being updated')
            #sensor.sensor_db_id = sensor_db_id
        
            if request.form.get("delete"):
                #delete record
                Sensors.query.filter_by(sensor_db_id=request.form.get("sensor_db_id")).delete()
                db.session.commit()
            else:
                #update the changes
                db.session.merge(sensor)
                db.session.commit()
        
        elif request.form.get("sensor_id") not in sensors_in_database:
            #insert record
            print('Sensor Count in merge:' + str(Sensors))    
            print('sensor is being inserted')
            db.session.add(sensor)
            db.session.commit()
            sensors_in_database.append(sensor.sensor_id)
               
        
    #here we have the normal behavior of the page
    #get all the sensors in database
    #get all sensors on the bus
    #compare the list of each against each other, place the non-assigned sensors at the top of the page maybe?
     
    print('starting sensor locations')
    #get all the possible sensor locations
    sensor_locations = SensorLocations.query.order_by(SensorLocations.sensor_location_value).all()
    #get all the possible sensor types
    sensor_types = SensorTypes.query.order_by(SensorTypes.sensor_type_value).all()
    
    from lib import OneWireSensors
    print('starting import from OneWireSensors')
    #get all sensors off the onewire bus
    sensor_ids_onewire = OneWireSensors.get_all_onewire_ids()
    
   
    print('starting loop through onewireids')
    for sensor_id in sensor_ids_onewire:
        if sensor_id not in sensors_in_database:
            sensor = Sensors(sensor_id = sensor_id)
            #insert record   
            db.session.add(sensor)
            db.session.commit()
            

    #pick up the changes before returning to page
    sensors = Sensors.query.order_by(Sensors.title).all()
    
    print('Finished loops')
    
    return render_template("sensors.html", sensors = sensors, sensor_locations=sensor_locations,sensor_types=sensor_types)

      

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
