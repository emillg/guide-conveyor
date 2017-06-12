#!/bin/sh
sudo pip install ibmiotf
echo Setting up the device configuration 
echo Please Enter Org ID
read ORG
echo Please Enter Device Type
read DEVICE_TYPE
echo Please Enter Device ID
read DEVICE_ID
echo please Enter Device Token
read DEVICE_TOKEN
echo "[device]" > device.conf
echo "org = $ORG" >>device.conf
echo "type = $DEVICE_TYPE" >>device.conf
echo "id = $DEVICE_ID" >>device.conf
echo "auth-method = token" >>device.conf
echo "auth-token  = $DEVICE_TOKEN" >>device.conf
echo You can edit the configurations stored in the device.conf file
echo Starting the device client program
python deviceClient.py
