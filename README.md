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
    scp -O -r ~/Workspace/pixelParty/raspberry-pi domroon@pixel-master.local:/home/domroon/pixelParty

## News API

https://newsapi.org


## SPI Communication
https://raspberrypi-aa.github.io/session3/spi.html
https://www.mathworks.com/help/supportpkg/raspberrypiio/spi-interface.html
https://www.takaitra.com/spi-device-raspberry-pi/
https://www.youtube.com/watch?v=dzVLRjH5i78
http://www.penguintutor.com/electronics/rpi-arduino-spi
https://www.sigmdel.ca/michel/ha/rpi/dnld/draft_spidev_doc.pdf
https://sigmdel.ca/michel/ha/rpi/spi_on_pi_en.html
https://github.com/WiringPi/WiringPi-Python

https://docs.micropython.org/en/latest/esp32/quickref.html#software-spi-bus


# I2C Communication
https://pypi.org/project/smbus2/

https://docs.micropython.org/en/latest/library/machine.I2C.html#machine-i2c


# UART Communication
https://www.electronicwings.com/raspberry-pi/raspberry-pi-uart-communication-using-python-and-c

# How to start the Parts of the Project

## RaspberryPi
- Start the RaspberryPi and start main.py in the raspberry-pi folder

## Computer
- Start the computer client in the computer-client folder with

        python -m uvicorn main:app --reload

- Start the mosquitto broker in /etc/mosquitto with

        mosquitto -c mosquitto.conf -v