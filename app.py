import os
import sys
#sys.path.append('/Adafruit_Python_GPIO')

# Import SPI library (for hardware SPI) and MCP3008 library.
import lib.Adafruit_GPIO.SPI as SPI
import lib.Adafruit_MCP3008 as MCP
import lib.Adafruit_MAX31855.MAX31855 as MAX31855
import time

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
from models import RPIPins, Sensors, SensorLocations, SensorTypes


@app.route('/')
def index():
    print('starting index')
    return render_template("index.html")

# Define a function to convert celsius to fahrenheit.
def c_to_f(c):
        return c * 9.0 / 5.0 + 32.0

@app.route('/create_database')
def create_database():
    from database_create import insert_initial_values_sensor_locations, insert_initial_values_sensor_types, insert_initial_RPIValues
    print('pre listen')
    #event.listen(SensorLocations.__table__, 'after_create', insert_initial_values_sensor_locations)
    #event.listen(SensorTypes.__table__, 'after_create', insert_initial_values_sensor_types)
 
    print('pre create')
    db.create_all()
    print('post create')

    insert_initial_values_sensor_locations()
    insert_initial_values_sensor_types()
    insert_initial_RPIValues()
    print('post values')
    return render_template("index.html")


@app.route('/sensors', methods=["GET", "POST"])
def sensors():
    print('Reading Sensors from DB')
    #get all sensors stored in the database
    sensors = Sensors.query.order_by(Sensors.title).all()
    
    print('Load DB Sensors into Array')
    #loop through all sensors saved in db and create an array of the sensor id's
    sensors_in_database = []
    for sensor in sensors:
        sensors_in_database.append(sensor.sensor_id)
    
    
    #if a form is posted we look for changes, and insert, update or delete
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
    
    #Load the sensor locations lookups & types lookups
    sensor_locations = SensorLocations.query.order_by(SensorLocations.sensor_location_value).all()
    sensor_types = SensorTypes.query.order_by(SensorTypes.sensor_type_value).all()
    rpipins = RPIPins.query.order_by(RPIPins.rpipins_id).all()


    #Now, sense all 1 Wires and Add them to DB
    from lib import OneWireSensors
    
    print('starting import from OneWireSensors')
    
    #get all sensors off the onewire bus
    sensor_ids_onewire = OneWireSensors.get_all_onewire_ids()
       
    for sensor_id in sensor_ids_onewire:
        if sensor_id not in sensors_in_database:
            sensor = Sensors(sensor_id = sensor_id)
            #insert record   
            db.session.add(sensor)
            db.session.commit()
    
    #from lib import Adafruit_MCP3008
    
    #Now, sense any data on the Analog Sensors and Add them to DB
    # Software SPI configuration:
    
    for  rpipin in rpipins:
        if rpipin.rpipins_type == "Analog" and rpipin.rpipins_clk is not None:
            
            
            CLK  = int(rpipin.rpipins_clk)
            MISO = int(rpipin.rpipins_miso)
            MOSI = int(rpipin.rpipins_mosi)
            CS   = int(rpipin.rpipins_cs)
        
            mcp = MCP.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

            print('Inspecting Analog for data')
        
            # Read all the ADC channel values in a list.
            values = [0]*8
            for i in range(8):
                # The read_adc function will get the value of the specified channel (0-7).
                values[i] = mcp.read_adc(i)
                voltage = (values[i]*5)/1024.0;
                if voltage > 0.4:
                    sensor = Sensors(sensor_id = 'A' + str(i))
                    #print('SensorID: ' + sensor)
                    if sensor.sensor_id not in sensors_in_database:
                        #insert record   
                        db.session.add(sensor)
                        db.session.commit()
                    
    
    
    #Now check for any MAX31855 Sensors
    x = 0
    for  rpipin in rpipins:
        if rpipin.rpipins_type == "MAX31855" and  rpipin.rpipins_clk is not None:
            x = x + 1
            
            # Raspberry Pi software SPI configuration.
            CLK  = int(rpipin.rpipins_clk)
            DO = int(rpipin.rpipins_miso)
            CS   = int(rpipin.rpipins_cs)
            maxsensor = MAX31855.MAX31855(CLK, CS, DO)

            
            sensor = Sensors(sensor_id = 'MAX31855-' + str(x))
            #print('SensorID: ' + sensor)
            if sensor.sensor_id not in sensors_in_database:
                #insert record   
                db.session.add(sensor)
                db.session.commit()
            
            #example code on reading from sensor
            temp = maxsensor.readTempC()
            internal = maxsensor.readInternalC()
            print('Thermocouple Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(temp, c_to_f(temp)))
            print('    Internal Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(internal, c_to_f(internal)))
               
                    
    
    #Finished finding all sensors.  Reload the Sensors object from the DB to pickup the new changes from above
    #pick up the changes before returning to page
    sensors = Sensors.query.order_by(Sensors.title).all()
    
    return render_template("sensors.html", sensors = sensors, sensor_locations=sensor_locations,sensor_types=sensor_types)




@app.route('/tables', methods=["GET", "POST"])
def rpipins():
    print('start table function')
    
    rpipins = RPIPins.query.order_by(RPIPins.rpipins_title).all()
    
    print('Load rpipins into Array')
    #loop through all sensors saved in db and create an array of the sensor id's
    
    for rpipin in rpipins:
        #sensors_in_database.append(sensor.sensor_id)
        print('instantiated rpipin')
    
    print('madeit')
    if request.form:
        print('request.form')
        #not triggering.. maybe put empty one there???
        rpipins_title = str(request.form.get("rpipins_title"))
        print(rpipins_title)
        if rpipins_title != '':
            #do the update. 
            print('updating values')
            rpipin = RPIPins(rpipins_title = rpipins_title
            , rpipins_id  = request.form.get("rpipins_id")
            , rpipins_type  = request.form.get("rpipins_type")
            , rpipins_number = request.form.get("rpipins_number")
            , rpipins_clk = request.form.get("rpipins_clk")
            , rpipins_cs = request.form.get("rpipins_cs")
            , rpipins_miso = request.form.get("rpipins_miso")
            , rpipins_mosi = request.form.get("rpipins_mosi"))
            
            print('rpi pin values set')
            db.session.merge(rpipin)
            db.session.commit()
        
        
            
            
    print('post values')
    return render_template("tables.html", rpipins = rpipins)



@app.route('/display')
def display():



    print('post values')
    return render_template("display.html")      

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
