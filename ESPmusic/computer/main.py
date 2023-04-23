import time
from logging import getLogger
from pathlib import Path

import paho.mqtt.client as mqtt
from pydub import AudioSegment
from pydub.playback import play

USERNAME = "domroon"
PASSWORD = "MPCkY5DGuU19sGgpvQvgYqN8Uw0"
CWD = Path.cwd()

COMPUTER_NAME = "computer"

logger = getLogger('mqttInput')
logger.setLevel(mqtt.MQTT_LOG_INFO)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print(f'Connected with result code {rc}')
    client.subscribe('led_matrix/#', qos=1)
    client.publish(f'{COMPUTER_NAME}/status', 'online', qos=1)

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
        print('MATRIX IS OFFLINE')
    if status == 'online':
        print('MATRIX IS ONLINE')


def main():
    broker_ip =  "192.168.73.72" # input('Please enter the IP of the Broker: ')
    song = AudioSegment.from_mp3(CWD / "Darude - Sandstorm.mp3")
    client = mqtt.Client(COMPUTER_NAME, clean_session=False)
    client.will_set(f'{COMPUTER_NAME}/status', 'offline', qos=1)
    client.username_pw_set(USERNAME, PASSWORD)
    client.enable_logger(logger=logger)

    # callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.message_callback_add('led_matrix/status', on_status)

    client.connect_async(broker_ip, 1884, 10)
    client.loop_start()
    
    while True:
        print('1 - Start Darude - Sandstorm')
        print('q - Exit')
        user_input = input('Input: \n')
        if user_input == '1':
            client.publish(f'{COMPUTER_NAME}/music', 'Darude-Sandstorm')
            play(song[1500:70000].fade_out(10000))
        elif user_input == 'q':
            client.publish(f'{COMPUTER_NAME}/status', 'offline', qos=1)
            client.disconnect()
            exit()

    
if __name__ == '__main__':
    main()