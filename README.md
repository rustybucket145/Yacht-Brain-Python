# known dependancies of the Yacht-Brain-Python web app

You will need a RaspberryPi available at adafruit
https://www.raspberrypi.org/products/

You will need to install Raspbian on the RaspberryPi (aka RPi)
https://www.raspberrypi.org/documentation/installation/installing-images/

Python 3
should come installed with Raspbian

Flask - a templating engine for Python
from the terminal run the following command to install flask
sudo apt-get install python3-flask

Bootstrap (css javascript...etc) - should all be included in file structure

Sqlite3 - database for storing data
https://iotbytes.wordpress.com/sqlite-db-on-raspberry-pi/
from the terminal run the following command
sudo apt-get install sqlite3

SQLAlchemy - database manager for flask somehow
https://www.pythoncentral.io/how-to-install-sqlalchemy/
from the terminal run the following commands (one at a time)
sudo apt-get install python3-sqlalchemy
sudo apt-get install python3-flask-sqlalchemy

Now you can clone the Yacht Brain for Python from git into your RPi
from the terminal run the following command
git clone https://github.com/rustybucket145/Yacht-Brain-Python.git


Now you should be able to navigate to the folder in your RPi:  
/home/pi/Yacht-Brain-Python

Getting started you will need to trigger your database to be created by firing
up the python3 server and visiting a few pages.

In terminal enter the following commands one at a time (pressing enter key after each)
cd /home/pi/Yacht-Brain-Python
python3 app.py

Our web server should now be online and active. To check visit the following url
In your browser

http://127.0.0.1:5000/create_database

The url above automagically creates the database and all database tables used in Yacht Brain

Now you can visit the actual dashboard by the following url
http://127.0.0.1:5000/

To setup your sensors just click the 'Sensors' link on the left side of the page.  
You will need to assing all sensors on your system. 
note:  If no sensors are shown it is bc none are connected to your RPi  

Connecting sensors will be covered at a later date.





