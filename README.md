## Links

- make your own pixel sprites https://www.piskelapp.com/

## MQTT Broker

On Windows:
C:\Program Files\mosquitto>mosquitto.exe -v -c mosquitto.conf
Set new Password for Broker: mosquitto_passwd.exe -H sha512 -c passwords domroon
Password for User "domroon": MPCkY5DGuU19sGgpvQvgYqN8Uw0
SSL-PW for Clients and Server: fPVYGc_Gss79T7vLSIyq2k7CLUE

## MQTT Website Connector

https://pypi.org/project/paho-mqtt/

## mosquitto.conf (unsecure - only for testing)

listener 1884
allow_anonymous true

## umqtt (micropython library)

https://mpython.readthedocs.io/en/master/library/mPython/umqtt.simple.html
https://github.com/micropython/micropython-lib/blob/master/micropython/umqtt.simple/umqtt/simple.py

## lcd display

https://microcontrollerslab.com/i2c-lcd-esp32-esp8266-micropython-tutorial/
https://peppe8o.com/download/micropython/LCD/lcd_api.py
https://peppe8o.com/download/micropython/LCD/i2c_lcd.py

## frozen modules and optimisation

### Description

To compile the project to a firmware go into the folder where the makefile live
(in the Debian WSL): ~/micropython/ports/esp32

    make BOARD=GENERIC FROZEN_MANIFEST=/mnt/c/workspace_local/Python/pixelParty/pixel_party_master/manifest.py

You can write the generated "firmware.bin" from the folder ~/micropython/ports/esp32/build-GENERIC write to the ESP32 with Thonny->Extras->Optionen

### Links

https://docs.micropython.org/en/latest/reference/manifest.html
https://www.udemy.com/course/micropython-python-fur-mikrocontroller-esp32-und-stm32/learn/lecture/25482454#overview
https://www.textfixer.de/html/html-komprimieren.php


## Copy Project on RaspberryPi

    scp -O -r ./pixelParty domroon@pixel-master.local:/home/domroon

## News API

https://newsapi.org
