# Uncomment one of the blocks of code below to configure your Pi or BBB to use
# software or hardware SPI.
import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855
import os
import glob
import Adafruit_MCP3008


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'

sensors = {
           'Probe 1': '28-020b924591df',
           'Probe 2': '28-020a92454cf1'
           };

# Software SPI configuration:
#CLK  = 18 
#MISO = 23
#MOSI = 24
#CS   = 25
#mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# Raspberry Pi software SPI configuration.
CLK = 13
CS  = 6
DO  = 5
sensor = MAX31855.MAX31855(CLK, CS, DO)

# Raspberry Pi software SPI configuration.
CLK2 = 13
CS2  = 6
DO2  = 5
sensor2 = MAX31855.MAX31855(CLK, CS, DO)
temp2 = 0

# Software SPI configuration:
pCLK  = 18 
MISO = 23
MOSI = 24
CS   = 25
mcp = Adafruit_MCP3008.MCP3008(clk=pCLK, cs=CS, miso=MISO, mosi=MOSI)

# Define a function to convert celsius to fahrenheit.
def c_to_f(c):
        return c * 9.0 / 5.0 + 32.0

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
    

# Loop printing measurements every second.
print('Press Ctrl-C to quit.')
while True:
    #thermo
    temp = sensor.readTempC()
    internal = sensor.readInternalC()
    print('Thermocouple1 Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(temp, c_to_f(temp)))
    print('       Board1 Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(internal, c_to_f(internal)))
    
    #temp2 = sensor.readTempC()
    internal2 = sensor2.readInternalC()
    print('Thermocouple2 Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(temp2, c_to_f(temp)))
    print('    Internal2 Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(internal2, c_to_f(internal)))
    
    #1 Wire 
    device_folder = glob.glob(base_dir + '*')[0]
    device_file = device_folder + '/w1_slave'
    for k, v in sensors.items():
        print(k,v)
        print(str(read_temp(v))+' '+k)
        
    # Read all the ADC channel values in a list. 
    values = [0]*8
    
    for i in range(8):
        # The read_adc function will get the value of the specified channel (0-7).
        values[i] = mcp.read_adc(i)
        #hook up 5v to first slot to read true 5.0 v
        #voltage = (values[i]*(values[1]/1024))/1024.0;
        voltage = (values[i]*5)/1024.0;
     
        if voltage > 0.25:
            print('Slot ' + str(i) + ':' + str(voltage));
    # Print the ADC values.
    # for 150 psi  .5 = 0psi  2.5v=75psi  4.5v=150psi
    # for 300 psi  .5 = 0psi  2.5v=150psi  4.5v=300psi
    
    print('=============================')
    time.sleep(1)

