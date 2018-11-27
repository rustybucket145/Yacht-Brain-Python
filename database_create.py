from app import app


from sqlalchemy import event, DDL
from shared import db

#import our data models
from models import Sensors, SensorLocations, SensorTypes




def insert_initial_values_sensor_locations():
    print('firing initial values for sensor locations')
    db.session.add(SensorLocations(sensor_location_value='', sensor_location_title='--select--'))
    db.session.add(SensorLocations(sensor_location_value='engine_single', sensor_location_title='Single Engine'))
    db.session.add(SensorLocations(sensor_location_value='engine_port', sensor_location_title='Port Engine'))
    db.session.add(SensorLocations(sensor_location_value='engine_stbd', sensor_location_title='Starboard Engine'))
    db.session.add(SensorLocations(sensor_location_value='generator1', sensor_location_title='Generator 1'))
    db.session.add(SensorLocations(sensor_location_value='generator2', sensor_location_title='Generator 2'))
    db.session.add(SensorLocations(sensor_location_value='salon', sensor_location_title='Salon'))
    db.session.add(SensorLocations(sensor_location_value='galley', sensor_location_title='Galley'))
    db.session.add(SensorLocations(sensor_location_value='bridge', sensor_location_title='Bridge'))
    db.session.add(SensorLocations(sensor_location_value='cockpit', sensor_location_title='Cockpit'))
    db.session.add(SensorLocations(sensor_location_value='engine_room', sensor_location_title='Engine Room'))
    db.session.add(SensorLocations(sensor_location_value='refrigeration', sensor_location_title='Referigeration'))
    db.session.add(SensorLocations(sensor_location_value='livewell', sensor_location_title='Livewell'))
    db.session.commit()
    
def insert_initial_values_sensor_types():
    print('firing initial values for sensor types')
    db.session.add(SensorTypes(sensor_type_value='', sensor_type_title='--select--'))
    db.session.add(SensorTypes(sensor_type_value='rpm', sensor_type_title='Livewell'))
    db.session.add(SensorTypes(sensor_type_value='coolantTemperature', sensor_type_title='Coolant Temp'))
    db.session.add(SensorTypes(sensor_type_value='oilTemperature', sensor_type_title='Oil Temp'))
    db.session.add(SensorTypes(sensor_type_value='transmissionOilTemperature', sensor_type_title='Transmission Oil Temp'))
    db.session.add(SensorTypes(sensor_type_value='exhaustTemperature', sensor_type_title='EGT'))
    db.session.add(SensorTypes(sensor_type_value='exhaustTemperatureInboard', sensor_type_title='EGT Inboard'))
    db.session.add(SensorTypes(sensor_type_value='exhaustTemperatureOutboard', sensor_type_title='EGT Outboard'))
    db.session.add(SensorTypes(sensor_type_value='alternatorVoltage', sensor_type_title='Alternator Voltage'))
    db.session.add(SensorTypes(sensor_type_value='oilPressure', sensor_type_title='Oil Pressure'))
    db.session.add(SensorTypes(sensor_type_value='coolantPressure', sensor_type_title='Coolant Pressure'))
    db.session.add(SensorTypes(sensor_type_value='boostPressure', sensor_type_title='Boost Pressure'))
    db.session.add(SensorTypes(sensor_type_value='transmissionOilPressure', sensor_type_title='Transmission Oil Pressure'))
    db.session.add(SensorTypes(sensor_type_value='fuelPressure', sensor_type_title='Fuel Pressure'))
    db.session.add(SensorTypes(sensor_type_value='crankcasePressure', sensor_type_title='Crankcase Pressure'))
    db.session.add(SensorTypes(sensor_type_value='runTime', sensor_type_title='Run Time')) 
    db.session.commit()
    
#event.listen(SensorLocations.__table__, 'after_create', insert_initial_values_sensor_locations)


#event.listen(SensorTypes.__table__, 'after_create', insert_initial_values_sensor_types)
    
