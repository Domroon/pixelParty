from umqtt.simple import MQTTClient
from machine import Pin, SoftSPI
import ubinascii
import machine
import micropython
import time

from ulogging import Logger
from networking import Client


pin_g2 = Pin(2, Pin.OUT, value=0)

# Default MQTT server to connect to
SERVER = input("Please enter MQTT Broker IP Address:")
CLIENT_ID = b"led-matrix-music"
COMPUTER_ID = "computer"
TOPIC = b"led-matrix-music/#"
TOPIC_2 = b"computer/#"
USER = 'domroon'
PASSWORD = 'MPCkY5DGuU19sGgpvQvgYqN8Uw0'

mqtt = MQTTClient(CLIENT_ID, SERVER, user=USER, password=PASSWORD, port=1884, keepalive=10)


def evaluate_message(topic, msg):
    topic = topic.decode('utf-8')
    msg = msg.decode('utf-8')
    print(topic, msg)
    
    if topic == f'{COMPUTER_ID}/music':
        print("Start Animation for", f'"{msg}"')

def main():    
    logger = Logger()
    client = Client(logger)
    client.activate()
    client.search_wlan()
    client.connect()
    # Subscribed messages will be delivered to this callback
    mqtt.set_callback(evaluate_message)
    mqtt.set_last_will(b"led_matrix/status", "offline", qos=1)
    mqtt.connect()
    mqtt.subscribe(TOPIC, qos=1)
    mqtt.subscribe(TOPIC_2, qos=1)
    mqtt.publish(b"led_matrix/status", "online", qos=1)

    counter = 0
    while True:
        try:
            # micropython.mem_info()
            print("Connected to %s, subscribed to %s topic" % (SERVER, TOPIC))
            while True:
                mqtt.check_msg()
                time.sleep(0.1)
                counter = counter + 1
                if counter == 100:
                    mqtt.ping()
                    counter = 0
        except OSError as error:
            print('OSError:', error)
            
        mqtt.disconnect()
        mqtt.connect()
        mqtt.subscribe(TOPIC, qos=1)
        print('Try again to connect to MQTT Broker')
        time.sleep(1)
        # client.disconnect()
        # client.deactivate()
        

if __name__ == '__main__':
    main()
