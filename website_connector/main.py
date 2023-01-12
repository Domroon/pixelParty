import time
from logging import getLogger
from pathlib import Path
import ssl

import paho.mqtt.client as mqtt

USERNAME = "domroon"
PASSWORD = "MPCkY5DGuU19sGgpvQvgYqN8Uw0"
CWD = Path.cwd() / 'website_connector'

logger = getLogger('mqttInput')
logger.setLevel(mqtt.MQTT_LOG_INFO)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print(f'Connected with result code {rc}')
    client.subscribe('led_matrix/#', qos=1)
    client.publish('website_connector/status', 'online', qos=1)

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")
    # client.subscribe("led")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(f'{msg.topic} {msg.payload}')


def on_log(client, userdata, level, buf):
    print(f'debug: {buf}')


def on_status(client, userdata, msg):
    status = msg.payload.decode('utf-8')
    if status == 'offline':
        # save it in a sqlite database
        print('MATRIX IS OFFLINE')
    if status == 'online':
        # save it in a sqlite database
        print('MATRIX IS ONLINE')


def main():
    broker_ip = input('Please enter the IP of the Broker: ')
    client = mqtt.Client('websiteConnector', clean_session=False)
    client.will_set('website_connector/status', 'offline', qos=1)
    client.username_pw_set(USERNAME, PASSWORD)
    # client.tls_set(ca_certs = CWD / 'ca.crt',
    #                certfile= CWD / 'client.crt',
    #                keyfile= CWD / 'client.key')
    client.enable_logger(logger=logger)

    # callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.message_callback_add('led_matrix/status', on_status)

    client.connect_async(broker_ip, 1884, 10)
    client.loop_start()
    
    while True:
        print('0 - Activate Debug Mode')
        print('1 - Restart LED Matrix')
        print('2 - Animation Mode')
        print('3 - Text Mode')
        print('4 - Picture Mode')
        print('5 - Weather Mode')
        print('6 - News Mode')
        print('7 - Multi')
        print('q - Exit')
        user_input = input('Input: \n')
        if user_input == '0':
            client.on_log = on_log
        elif user_input == '1':
            client.publish('website_connector/command', 'restart')
        elif user_input == '2':
            client.publish('website_connector/modus', 'animation')
            print('Animationsmodis')
            print('a - line_top_bottom')
            print('b - full_color')
            print('c - full_fade_in')
            print('d - color_change')
            print('e - random_colors')
            print('f - random_color_flash')
            modus = input('Bitte einen Modus eingeben (a-f): ')
            client.publish('website_connector/modus/animation/data', f'{modus}')
        elif user_input == '3':
            client.publish('website_connector/modus', 'text')
            text = input("Bitte einen Text eingeben: ")
            time.sleep(1)
            client.publish('website_connector/modus/text/data', f'{text}')
        elif user_input == '4':
            client.publish('website_connector/modus', 'picture')
            print("Bitte das anzuzeigende Bild als 'pixels'-Datei im Ordner")
            print("pixelparty/website_connector/pixels_data abspeichern")
            pixels_data_name = input("Bitte den Namen der Datei eingeben:")
            path = CWD / 'pixels_data' / pixels_data_name
            with open(path, 'r') as file:
                pixels_data = file.read()
                client.publish("website_connector/modus/picture/data", f'{pixels_data}')
        elif user_input == '5':
            client.publish('website_connector/modus', 'weather')
            time.sleep(1)
            client.publish("website_connector/modus/weather/data", "weather data")
        elif user_input == '6':
            client.publish('website_connector/modus', 'news')
            time.sleep(1)
            client.publish("website_connector/modus/news/data", "news data")
        elif user_input == '7':
            client.publish('website_connector/modus', 'multi')
            print("Bitte die Modis eingeben, welche angezeigt werden sollen (getrennt mit einem Komma)")
            modis = input('animation/text/picture/weather/news (zuletzt Zeit in s):')
            client.publish("website_connector/modus/multi/data", f'{modis}')
        elif user_input == 'q':
            client.publish('website_connector/status', 'offline', qos=1)
            client.disconnect()
            exit()

    
if __name__ == '__main__':
    main()