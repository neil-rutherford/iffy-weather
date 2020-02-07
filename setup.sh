#!/bin/bash

# CHECKING SUDO PERMISSIONS

if sudo echo "SUDO TEST" | grep "This incident will be reported."
then
	echo "ERROR: Broken sudo."
	exit
fi

# CHECK PYTHON, SET UP VIRTUAL ENVIRONMENT, & INSTALL DEPENDENCIES

sudo apt-get install python3
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt

# INSTALL CUSTOM DEPENDENCY FOR HUMIDITY SENSOR

sudo apt-get install git-core
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
sudo apt-get install build-essential python-dev
sudo python3 setup.py install

# INITIALIZE ACCESS POINT (ASSUMING THE FOLLOWING PREREQS:)
# - STATIC IP HAS BEEN CONFIGURED
# - DHCP SERVER HAS BEEN CONFIGURED
# - HOSTAPD SERVER HAS BEEN CONFIGURED
# MORE INFO HERE: https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md

sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd

# I'M NOT SURE HOW TO GET THE WIFI NETWORK CREDS FROM THE APP TO MAKE THE BRIDGE
