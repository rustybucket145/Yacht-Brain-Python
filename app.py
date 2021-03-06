#sys.path.append('/Adafruit_Python_GPIO')
import os
import sys
import cgi, cgitb

# Import SPI library (for hardware SPI) and MCP3008 library.
import lib.Adafruit_GPIO.SPI as SPI
import lib.Adafruit_MCP3008 as MCP
import lib.Adafruit_MAX31855.MAX31855 as MAX31855
import time
import glob


from flask import Flask, render_template, request, json
from flask_socketio import SocketIO, emit

from random import random
from threading import Thread, Event

from sqlalchemy import event, DDL

base_dir = '/sys/bus/w1/devices/'
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir,"yachtbraindatabase.db"))
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

#turn the flask app into a socketio app
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()


from shared import db
db.init_app(app)
x=0
#import our data models
from models import RPIPins, Sensors, SensorLocations, SensorTypes


# Define a function to convert celsius to fahrenheit.
def c_to_f(c):
        return c * 9.0 / 5.0 + 32.0

#used for 1Wire 
def read_temp_raw(device_file):
    
    
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

#used for 1Wire
def read_temp(sensor_id):
    print(sensor_id)
    
    import os.path
    if os.path.exists(base_dir + sensor_id):
        
        device_folder = glob.glob(base_dir + sensor_id)[0]
        device_file = device_folder + '/w1_slave'
    
    
    
        lines = read_temp_raw(device_file)
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw(device_file)
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
        
            data = {"temp_c": round(temp_c), "temp_f": round(temp_f)}
        
        
            return data
    else:
        data = {"temp_c": "9999", "temp_f": "9999"} 
        return data



#used for 1Wire
def read_temp_return_list(sensor_id):
    print(sensor_id)
    
    import os.path
    if os.path.exists(base_dir + sensor_id):
        
        device_folder = glob.glob(base_dir + sensor_id)[0]
        device_file = device_folder + '/w1_slave'
    
    
    
        lines = read_temp_raw(device_file)
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw(device_file)
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
        
            data = {"temp_c": round(temp_c), "temp_f": round(temp_f)}
            #data = {}
            #data.temp_c = round(temp_c)
            #data.temp_f = round(temp_f)
            
        
            return data
    else:
        #data = {}
        #data.temp_c = round(999)
        #data.temp_f = round(888)
        data = {"temp_c": round(999), "temp_f": round(888)}   
        return data


def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

# -  PAGE Functions

@app.route('/')
def index():
    print('starting index')
    return render_template("index.html")


@app.route('/create_database')
def create_database():
    from database_create import insert_initial_values_sensor_locations, insert_initial_values_sensor_types, insert_initial_RPIValues

    db.create_all()

    insert_initial_values_sensor_locations()
    insert_initial_values_sensor_types()
    insert_initial_RPIValues()
    
    return render_template("index.html")


@app.route('/sensors', methods=["GET", "POST"])
def sensors():
    print('Reading Sensors from DB')
    #get all sensors stored in the database
    sensors = Sensors.query.order_by(Sensors.title).all()
    #print(type(sensors))
    print('Load DB Sensors into Array')
    #loop through all sensors saved in db and create an array of the sensor id's
    sensors_in_database = []
    for sensor in sensors:
        sensors_in_database.append(sensor.sensor_id)
    
    
    #if a form is posted we look for changes, and insert, update or delete
    if request.form:
        print('form was posted')
        sensor_db_id = request.form.get("sensor_db_id")

        # , sensor_id = request.form.get("sensor_id")  - removed this so they cant overwrite it - used for sensor reads
        # read values from form
        sensor = Sensors(title = request.form.get("title")
        , sensor_db_id = request.form.get("sensor_db_id")
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
            if request.form.get("delete"):
                #delete record
                Sensors.query.filter_by(sensor_db_id=request.form.get("sensor_db_id")).delete()
                db.session.commit()
            else:
                #update the changes
                db.session.merge(sensor)
                db.session.commit()
        
        elif request.form.get("sensor_id") not in sensors_in_database:
            #its a new one, insert record
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
    
    #get all sensors off the onewire bus
    sensor_ids_onewire = OneWireSensors.get_all_onewire_ids()
       
    for sensor_id in sensor_ids_onewire:
        if sensor_id not in sensors_in_database:
            sensor = Sensors(sensor_id = sensor_id)
            #insert record   
            db.session.add(sensor)
            db.session.commit()
    
    #Now, sense any data on the Analog Sensors and Add them to DB
    for  rpipin in rpipins:
        if rpipin.rpipins_type == "Analog" and rpipin.rpipins_clk is not None and rpipin.rpipins_clk != 'None':
            
            BoardNum = rpipin.rpipins_number
            CLK  = int(rpipin.rpipins_clk)
            MISO = int(rpipin.rpipins_miso)
            MOSI = int(rpipin.rpipins_mosi)
            CS   = int(rpipin.rpipins_cs)
        
            mcp = MCP.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

            print('Inspecting Analog for data')
            # Read all the ADC channel values in a list.
            values = [0]*8
            for i in range(8):
                print('looping analog')
                # The read_adc function will get the value of the specified channel (0-7).
                values[i] = mcp.read_adc(i)
                voltage = (values[i]*5)/1024.0;
                print('voltage' + str(voltage))
                if voltage > 0.2:
                    sensor = Sensors(sensor_id = 'A' + str(i) + '-' + str(BoardNum))
                    #print('SensorID: ' + sensor)
                    if sensor.sensor_id not in sensors_in_database:
                        #insert record   
                        db.session.add(sensor)
                        db.session.commit()
                    
    
    
    #Now check for any MAX31855 Sensors
    x = 0
    for  rpipin in rpipins:
        if rpipin.rpipins_type == "MAX31855" and  rpipin.rpipins_clk is not None and rpipin.rpipins_clk != 'None': 
            x = x + 1
            
            # Raspberry Pi software SPI configuration.
            CLK  = int(rpipin.rpipins_clk)
            DO = int(rpipin.rpipins_miso)
            CS   = int(rpipin.rpipins_cs)
            maxsensor = MAX31855.MAX31855(CLK, CS, DO)

            sensor = Sensors(sensor_id = 'MAX31855-' + str(x))

            if sensor.sensor_id not in sensors_in_database:
                #insert record   
                db.session.add(sensor)
                db.session.commit()
            
            #example code on reading from sensor
##            temp = maxsensor.readTempC()
##            internal = maxsensor.readInternalC()
##            print('Thermocouple Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(temp, c_to_f(temp)))
##            print('    Internal Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(internal, c_to_f(internal)))
               
                    
    
    #Finished finding all sensors.  Reload the Sensors object from the DB to pickup the new changes from above
    #pick up the changes before returning to page
    sensors = Sensors.query.order_by(Sensors.title).all()
    import pprint
    pprint.pprint(sensors)
    return render_template("sensors.html", sensors = sensors, sensor_locations=sensor_locations,sensor_types=sensor_types)




@app.route('/tables', methods=["GET", "POST"])
def rpipins():

    rpipins = RPIPins.query.order_by(RPIPins.rpipins_title).all()

    #loop through all sensors saved in db and create an array of the sensor id's
    for rpipin in rpipins:
        #sensors_in_database.append(sensor.sensor_id)
        print('instantiated rpipin')
    
    if request.form:
        rpipins_title = str(request.form.get("rpipins_title"))
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
            
    return render_template("tables.html", rpipins = rpipins)


##import cgi, cgitb
##print "Content-type: text/html\n\n"    #for showing print on HTML
##data = cgi.FieldStorage()
##argument = data["webArguments"].value    #argument = name of PLC i need to fetch
###some script for connecting to PLC and reading current value of 
###variable  with name "argument", in this example "aiTemperature"
##print plcVar











#ajax function to retrieve sensor values based on sensor id
@app.route('/getSensorValue', methods=["GET", "POST"])
def getSensorValue():
    print('sensor value')
    
    #sensor_id = request.GET['sensor_id']
    sensor_id = request.values['sensor_id']
    sensor_value = read_temp(sensor_id)
    #print(sensor_value)
    import json

    #data = json.loads(sensor_value)

    #print(data)



    return json.dumps(sensor_value)




#ajax function to retrieve sensor values based on sensor id
def getSensorValueForSocket(sensor):
    print('sensor value')
    
    #sensor_id = request.GET['sensor_id']
    #if 'sensor_id' in locals():
        #sensor_id = request.values['sensor_id']
            
    return read_temp_return_list(sensor.sensor_id)
    #print(sensor_value)
    #import json

    #data = json.loads(sensor_value)

    #print(data)



    #return sensor_value
    #return json.dumps(sensor_value)





@app.route('/UpdateGauges', methods=['POST'])
def UpdateGauges():
    
    #get all sensors stored in the database
    sensors = Sensors.query.order_by(Sensors.title).all()
    
    ScreenText = []

    #loop through all sensors saved in db and create an array of the sensor id's
    for sensor in sensors:
               
        #Display them all now to screen
        if sensor.is_one_wire == 1:
            #1 Wire 
            device_folder = glob.glob(base_dir + '*')[0]
            device_file = device_folder + '/w1_slave'
            #print(sensor.title + ' : ' + str(read_temp(sensor.sensor_id)) + 'F')
            ScreenText.append(str(int(read_temp(sensor.sensor_id))) + '°F')
            
        elif sensor.is_analog_sensor == 1:
            
            #which board is this, and find right pins for it
            BoardNum = right(sensor.sensor_id,1)
            
            #now do a lookup from rpipins to find Analog pins for that board
            rpipins = RPIPins.query.order_by(RPIPins.rpipins_id).all()
            
            for rpipin in rpipins:
                if rpipin.rpipins_type == 'Analog' and rpipin.rpipins_number == str(BoardNum):
                    
                    # Software SPI configuration:
                    pCLK  = int(rpipin.rpipins_clk)
                    MISO = int(rpipin.rpipins_miso)
                    MOSI = int(rpipin.rpipins_mosi)
                    CS   = int(rpipin.rpipins_cs)
                    mcp = MCP.MCP3008(clk=pCLK, cs=CS, miso=MISO, mosi=MOSI)
            
            # The read_adc function will get the value of the specified channel (0-7).
            voltage = mcp.read_adc(int(right(left(sensor.sensor_id,2),1)))
            
            #hook up 5v to first slot to read true 5.0 v
            voltage = (voltage*5)/1024.0;
         
            #if voltage > 0.25:
            pressure = 0
            if voltage > .5:
                # example multiplier for 150psi sensor
                pressure = voltage * 30
            
            #print(sensor.title + ' : ' + str(pressure) + 'psi');
            ScreenText.append(str(pressure) + 'psi')
            
            #need to look up the other sensor settings to determine voltage scale still
            # Print the ADC values.
            # for 150 psi  .5 = 0psi  2.5v=75psi  4.5v=150psi
            # for 300 psi  .5 = 0psi  2.5v=150psi  4.5v=300psi
            
            
        elif left(sensor.sensor_id,8) == 'MAX31855':
            
            #which board is this, and find right pins for it
            BoardNum = right(sensor.sensor_id,1)
            
            #now do a lookup from rpipins to find Analog pins for that board
            rpipins = RPIPins.query.order_by(RPIPins.rpipins_id).all()
            
            for rpipin in rpipins:
                if rpipin.rpipins_type == 'MAX31855' and rpipin.rpipins_number == str(BoardNum):
                    # Raspberry Pi software SPI configuration.
                    CLK  = int(rpipin.rpipins_clk)
                    DO = int(rpipin.rpipins_miso)
                    CS   = int(rpipin.rpipins_cs)
                    maxsensor = MAX31855.MAX31855(CLK, CS, DO)

            #example code on reading from sensor
            temp = maxsensor.readTempC()
            internal = maxsensor.readInternalC()
            #print(sensor.title + ' Probe Temp: ' +  str(c_to_f(temp)))
            #print(sensor.title + ' Board Temp: ' +  str(c_to_f(internal)))
            if temp != temp:
                #checking for Nan (not a number)
                temp = 0
            if internal != internal:
                #checking for Nan (not a number)
                internal = 0
            ScreenText.append(str(int(c_to_f(temp))) + '°F')
            ScreenText.append(str(int(c_to_f(internal))) + '°F')
            
   
    return json.dumps({'GaugeValues':ScreenText})
#    return json.dumps({'GaugeValues':ScreenText,'Temp2':str(c_to_f(temp))})
 


@app.route('/display_twin_engine')
def display_twin_engine():

    #get all sensors stored in the database
    sensors = Sensors.query.order_by(Sensors.title).all()

    sensor_locations = SensorLocations.query.order_by(SensorLocations.sensor_location_value).all()
    sensor_types = SensorTypes.query.order_by(SensorTypes.sensor_type_value).all()
    rpipins = RPIPins.query.order_by(RPIPins.rpipins_id).all()


    return render_template("display_twin_engine.html", sensors=sensors, sensor_types=sensor_types)


@app.route('/display')
def display():

    #get all sensors stored in the database
    sensors = Sensors.query.order_by(Sensors.title).all()
    
    ScreenText = []

    #loop through all sensors saved in db and create an array of the sensor id's
    for sensor in sensors:
               
        #Display them all now to screen
        if sensor.is_one_wire == 1:
            #1 Wire 
            device_folder = glob.glob(base_dir + '*')[0]
            device_file = device_folder + '/w1_slave'
            #print(sensor.title + ' : ' + str(read_temp(sensor.sensor_id)) + 'F')
            ScreenText.append(sensor.title)
            
        elif sensor.is_analog_sensor == 1:
            
            #which board is this, and find right pins for it
            BoardNum = right(sensor.sensor_id,1)
            
            #now do a lookup from rpipins to find Analog pins for that board
            rpipins = RPIPins.query.order_by(RPIPins.rpipins_id).all()
            
            for rpipin in rpipins:
                if rpipin.rpipins_type == 'Analog' and rpipin.rpipins_number == str(BoardNum):
                    
                    # Software SPI configuration:
                    pCLK  = int(rpipin.rpipins_clk)
                    MISO = int(rpipin.rpipins_miso)
                    MOSI = int(rpipin.rpipins_mosi)
                    CS   = int(rpipin.rpipins_cs)
                    mcp = MCP.MCP3008(clk=pCLK, cs=CS, miso=MISO, mosi=MOSI)
            
            # The read_adc function will get the value of the specified channel (0-7).
            voltage = mcp.read_adc(int(right(left(sensor.sensor_id,2),1)))
            
            #hook up 5v to first slot to read true 5.0 v
            voltage = (voltage*5)/1024.0;
         
            #if voltage > 0.25:
            pressure = 0
            if voltage > .5:
                # example multiplier for 150psi sensor
                pressure = voltage * 30
            
            #print(sensor.title + ' : ' + str(pressure) + 'psi');
            ScreenText.append(sensor.title)
            
            #need to look up the other sensor settings to determine voltage scale still
            # Print the ADC values.
            # for 150 psi  .5 = 0psi  2.5v=75psi  4.5v=150psi
            # for 300 psi  .5 = 0psi  2.5v=150psi  4.5v=300psi
            
            
        elif left(sensor.sensor_id,8) == 'MAX31855':
            
            #which board is this, and find right pins for it
            BoardNum = right(sensor.sensor_id,1)
            
            #now do a lookup from rpipins to find Analog pins for that board
            rpipins = RPIPins.query.order_by(RPIPins.rpipins_id).all()
            
            for rpipin in rpipins:
                if rpipin.rpipins_type == 'MAX31855' and rpipin.rpipins_number == str(BoardNum):
                    # Raspberry Pi software SPI configuration.
                    CLK  = int(rpipin.rpipins_clk)
                    DO = int(rpipin.rpipins_miso)
                    CS   = int(rpipin.rpipins_cs)
                    maxsensor = MAX31855.MAX31855(CLK, CS, DO)

            #example code on reading from sensor
            temp = maxsensor.readTempC()
            internal = maxsensor.readInternalC()
            #print(sensor.title + ' Probe Temp: ' +  str(c_to_f(temp)))
            #print(sensor.title + ' Board Temp: ' +  str(c_to_f(internal)))
            ScreenText.append(sensor.title + ' Probe Temp')
            ScreenText.append(sensor.title + ' Board Temp')
            
            
    return render_template("display.html", ScreenText = ScreenText)      





#sockets test script
def sensorReadValueToSocket(sensors):
    """
    continually loop through sensors and take readings
    push the values to the web socket to update any clients
    
    """
    #print('getting sensors')
    # get all the sensors in the database
    #with app.app_context():
        #sensors = Sensors.query.order_by(Sensors.title).all()
    #from pprint import pprint
    #type(sensors)
    
    #print('got sensors')
    #infinite loop of magical random numbers
    #print("checkign sensors")
    
    import json
    
    while not thread_stop_event.isSet():
        
        for i in range(len(sensors)):
            #print(type(sensors[i]))
            #print(sensors[i].sensor_id)
        
            #print('sensor for')
            #sensor_data = sensors[i]
            
            #data = json.dumps(sensors[i])
            
            #sensors[i].sensorValues = getSensorValueForSocket(sensors[i])
            #sensor_data.sensorValue = 132
            
            #print(sensors[i].sensor_id)
            #print('got endfor sensors')
            
            sensor_json = {
                "sensor_id": sensors[i].sensor_id
                , "sensor_values": getSensorValueForSocket(sensors[i])                
                , "sensor_db_id": sensors[i].sensor_db_id
                , "title": sensors[i].title
                , "sensor_location": sensors[i].sensor_location
                , "sensor_type": sensors[i].sensor_type
                , "warning_low": sensors[i].warning_low
                , "warning_hi": sensors[i].warning_hi
                , "alarm_low": sensors[i].alarm_low
                , "alarm_hi": sensors[i].alarm_hi
                , "mapping_a_reading": sensors[i].mapping_a_reading
                , "mapping_a_value": sensors[i].mapping_a_value
                , "mapping_b_reading": sensors[i].mapping_b_reading
                , "is_one_wire": sensors[i].is_one_wire
                , "is_analog_sensor": sensors[i].is_analog_sensor
                }
            
            
            socketio.emit('newnumber', sensor_json, namespace='/test')
        
        #sensor_data.sensorValue = 321
        #socketio.emit('newnumber', {'number': sensor_data.sensorValue}, namespace='/test')              
        socketio.sleep(5)



def randomNumberGenerator():
    """
    Generate a random number every 1 second and emit to a socketio instance (broadcast)
    Ideally to be run in a separate thread?
    """
    #infinite loop of magical random numbers
    print("Making random numbers")
    
    with app.app_context():
        sensors = Sensors.query.order_by(Sensors.title).all()
    
    
    print("Mxxxxxs")
    while not thread_stop_event.isSet():
        number = round(random()*10, 3)
        print(number)
        socketio.emit('newnumber', {'number': number}, namespace='/test')
        socketio.sleep(2)


@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    if not thread.isAlive():
        print("Starting Thread")
        
        sensors = Sensors.query.order_by(Sensors.title).all()
        thread = socketio.start_background_task(sensorReadValueToSocket, sensors)

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
