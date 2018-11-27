
import os
import glob
import time

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'

sensors = {
           'temp-test': '28-0315901e06ff'
           };

def read_temp_raw(device_file):
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp(sensor_id):
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
        return int(round(temp_f))



def get_all_onewire_ids():
    folders = []
    for entry in os.scandir(base_dir):
        if (entry.is_dir() and entry.name != 'w1_bus_master1'):
            folders.append(entry.name)
        
    return(folders)
    


	
#while True:
 
    #device_folder = glob.glob(base_dir + '*')[0]
    #device_file = device_folder + '/w1_slave'

 #   for k, v in sensors.items():
        #print(k,v)
        
    
 #       print(str(read_temp(v))+' '+k)	


  #  print('=============================')
  #  time.sleep(2)

