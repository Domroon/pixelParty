import time
from logging import getLogger
from pathlib import Path
import ssl

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

USERNAME = "domroon"
PASSWORD = "MPCkY5DGuU19sGgpvQvgYqN8Uw0"
CWD = Path.cwd()
DEVICE_NAME = 'computer-client'
MATRIX_NAME = 'pixel-master'

logger = getLogger('mqttInput')
logger.setLevel(mqtt.MQTT_LOG_INFO)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print(f'Connected with result code {rc}')
    client.subscribe(f'{MATRIX_NAME}/#', qos=1)
    client.publish(f'{DEVICE_NAME}/status', 'online', qos=1)

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")
    # client.subscribe("led")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(f'{msg.topic} {msg.payload}')


# def on_log(client, userdata, level, buf):
#     print(f'debug: {buf}')


def on_status(client, userdata, msg):
    status = msg.payload.decode('utf-8')
    if status == 'offline':
        # save it in a sqlite database
        print('MATRIX IS OFFLINE')
    if status == 'online':
        # save it in a sqlite database
        print('MATRIX IS ONLINE')


def main():
    print(CWD)
    broker_ip = 'localhost' #input('Please enter the IP of the Broker: ')
    client = mqtt.Client('computer_client', clean_session=False)
    client.will_set(f'{DEVICE_NAME}/status', 'offline', qos=1)
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
        # print('0 - Activate Debug Mode')
        print('1 - Reset LED Matrix')
        print('2 - Show ScrollText')
        print('3 - Show Animation')
        print('4 - Show Picture')
        print('5 - Show Weather')
        print('6 - Show News')
        # print('7 - Show a List of ScreenObjects')
        print('q - Exit')
        user_input = input('Input: \n')
        # if user_input == '0':
        #     client.on_log = on_log
        if user_input == '1':
            client.publish(f'{MATRIX_NAME}/reset', '')
        elif user_input == '2':
            text = input('Please Enter a Text: ')
            client.publish(f'{MATRIX_NAME}/scroll_text', text)
        elif user_input == '3':
            print('Please choose an Animation')
            print('a - random_colors')
            print('b - random_color_flash')
            user_ani = input('Input: \n')
            while True:
                if user_ani == 'a':
                    client.publish(f'{MATRIX_NAME}/animation', 'random_colors')
                    break
                elif user_ani == 'b':
                    sleep_time = input('Please Enter a sleep time between the flashing in seconds: ')
                    client.publish(f'{MATRIX_NAME}/animation', f'random_color_flash,{sleep_time}')
                    break
                else:
                    print('Wrong Input. Try again.')
        elif user_input == '4':
            picture_name = input('Please Enter a Filename from a Picture in the "Picture"-Folder: ')
            with open(CWD / 'pictures' / picture_name, 'rb') as file:
                fileContent = file.read()
                byteArr = bytearray(fileContent)
                client.publish(f'{MATRIX_NAME}/picture', byteArr)
        elif user_input == '5':
            city_name = input('Please enter a City Name: ')
            client.publish(f'{MATRIX_NAME}/weather', city_name)
        elif user_input == '6':
            source_id = input('Please enter a news source id: ')
            client.publish(f'{MATRIX_NAME}/news', source_id)
        elif user_input == 'q':
            client.publish(f'{DEVICE_NAME}/status', 'offline', qos=1)
            client.disconnect()
            exit()
        else:
            print('Wrong Input. Try again.')
        
    
if __name__ == '__main__':
    main()