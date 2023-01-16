- [x] implement change_all_color
- [ ] add a sprite_method that translate a string into pixel-graphic-signs and add it to pixels of a sprite object (method_name: add_string_graphic?)
- [ ] implement a clock class (should do all the sprite stuff)
- [x] implement brightness parameter for Pixel Objects (maybe a max value for r, g, b instead a multiplicator?)
- [x] implement add_colored_pixels
- [x] add pixels data for all letter and digits (upper-case)
- [x] reduce the "flickering effect" by only clear single sprite-object instead the whole matrix
- [x] add a python program that convert a pixel-picture into a color-array

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

## to do

- EN-pin vom matrix esp32 kann mit masse verbunden werden um ihn neu zu starten
- transistor verwenden um einen neustart über einen ausgangspin des mqtt_esp32 zu erwirken
- nach dem neustart sollen sich beide esp32 über den i2c-bus verbinden und es soll übermittelt werden (ein string?), was über
  den mqtt-broker vom anderen mqtt-client(website-connector) angekommen ist
- zuerst den website connector mit einem topic 'led-matrix' ausstatten und der message 'restart'
- dann in der mqtt_esp32-software bei der ankunft von 'restart' über den topic 'led-matrix' den esp32_matrix neu starten
- website_connector und mqtt_esp32 müssen natürlich auf 'led-matrix' subscriben
- allein ein publish auf ein topic reicht um auf dieses ein subscribe zu haben
- ein 'is_alive' topic errichten (beide subscriben) und alle 60 sekunden anfragen ob die matrix verbunden ist (auf
  def website soll dann entsprechend angezeigt werden können ob das gerät online oder offline ist) (!bereits in bibliothek implementiert mit keepalive!)
- ein javascript-programm ist vermutlich die beste wahl
- so kann mit simplem html und css gearbeitet werden
- oder doch lieber flask weil simpel?? AUSTESTEN!! und weiter überlegen ;)
- ankommende messages am mqtt_esp32 in eine liste (hier queue) schreiben um diese in einem seperaten thread abarbeiten zu können!
