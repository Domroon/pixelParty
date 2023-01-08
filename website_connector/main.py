import time
from logging import getLogger
from pathlib import Path
import ssl

import paho.mqtt.client as mqtt

BROKER_IP = "192.168.152.168"
USERNAME = "domroon"
PASSWORD = "MPCkY5DGuU19sGgpvQvgYqN8Uw0"
CWD = Path.cwd() / 'website_connector'

logger = getLogger('mqttInput')
logger.setLevel(mqtt.MQTT_LOG_INFO)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print(f'Connected with result code {rc} to {BROKER_IP}')
    client.subscribe('led_matrix/#', qos=1)

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")
    # client.subscribe("led")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(f'{msg.topic} {msg.payload}')


def on_log(client, userdata, level, buf):
    print(f'log: {buf}')


def main():
    client = mqtt.Client('websiteConnector')
    client.username_pw_set(USERNAME, PASSWORD)
    # client.tls_set(ca_certs = CWD / 'ca.crt',
    #                certfile= CWD / 'client.crt',
    #                keyfile= CWD / 'client.key')
    client.enable_logger(logger=logger)

    # callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_log = on_log

    client.connect_async(BROKER_IP, 1884, 10)
    client.loop_start()
    
    while True:
        print('1 - Restart LED Matrix')
        print('q - Exit')
        user_input = input('Input: ')
        if user_input == '1':
            client.publish('led_matrix', 'restart')
        elif user_input == 'q':
            exit()

    
if __name__ == '__main__':
    main()