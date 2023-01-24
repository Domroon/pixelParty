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
