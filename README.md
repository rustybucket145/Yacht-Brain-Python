# known dependancies of the Yacht-Brain-Python web app

You will need a RaspberryPi available at adafruit
https://www.raspberrypi.org/products/

You will need to install Raspbian on the RaspberryPi (aka RPi)
https://www.raspberrypi.org/documentation/installation/installing-images/

Python 3
should come installed with Raspbian

Now you can clone the Yacht Brain for Python from git into your RPi
from the terminal run the following command
git clone https://github.com/rustybucket145/Yacht-Brain-Python.git

// create the virtual environement
cd Yacht-Brain-Python
python3 -m venv venv
// activate the virtual environment
. venv/bin/activate


Flask - a templating engine for Python
from the terminal run the following command to install flask
sudo apt-get install python3-flask

// install flask socketio, this allows for web sockets
pip install flask-socketio

Bootstrap (css javascript...etc) - should all be included in file structure

Sqlite3 - database for storing data
https://iotbytes.wordpress.com/sqlite-db-on-raspberry-pi/
from the terminal run the following command
sudo apt-get install sqlite3

SQLAlchemy - database manager for flask somehow
https://www.pythoncentral.io/how-to-install-sqlalchemy/
from the terminal run the following command
pip install sqlalchemy


///this does not work yet
Install espeak by running the following commands
this will allow your rpi to give verbal warnings/alarms when sensors reach alarm status
sudo apt-get install espeak
chromium-browser --enable-speech-dispatcher
//////



Now you should be able to navigate to the folder in your RPi:  
/home/pi/Yacht-Brain-Python

Getting started you will need to trigger your database to be created by firing
up the python3 server and clicking a link on the home page.

Launch the app as follows:
In terminal enter the following commands one at a time (pressing enter key after each)
cd /home/pi/Yacht-Brain-Python
. venv/bin/activate
python3 app.py

Our web server should now be online and active. To check visit the following url
In your browser

http://127.0.0.1:5000/

Click the Create Database URL which automagically creates the database and all database tables used in Yacht Brain

Now click on the Board/Pin Assignments tab.  Here you will assign which pins your Analog and other boards utilize.

Finally, to setup your sensors just click the 'Sensors' link on the left side of the page.  
You will need to assing all sensors on your system. 
note:  If no sensors are shown it is bc none are connected to your RPi  

Connecting sensors will be covered at a later date.





