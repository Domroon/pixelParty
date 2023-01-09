from umqtt.simple import MQTTClient
from machine import Pin
import ubinascii
import machine
import micropython
import time

from ulogging import Logger
from networking import Client


pin_g2 = Pin(2, Pin.OUT, value=0)

# Default MQTT server to connect to
SERVER = "192.168.110.168"
CLIENT_ID = b"matrix-" + ubinascii.hexlify(machine.unique_id())
TOPIC = b"led_matrix/#"
TOPIC_2 = b"website_connector/#"
USER = 'domroon'
PASSWORD = 'MPCkY5DGuU19sGgpvQvgYqN8Uw0'

mqtt = MQTTClient(CLIENT_ID, SERVER, user=USER, password=PASSWORD, port=1884, keepalive=10)


def evalute_message(topic, msg):
    topic = topic.decode('utf-8')
    msg = msg.decode('utf-8')
    print(topic, msg)
    
    # den status zu publishen ist 
    # unnötig da nachrichten für den website_connector
    # auf dem broker zwischengespeichert werden
    # falls dieser nicht online ist
    # if topic == 'website_connector/status':
    #     if msg == 'online':
    #         mqtt.publish('led_matrix/status', 'online', qos=1)


def main():    
    logger = Logger()
    client = Client(logger)
    client.activate()
    client.search_wlan()
    client.connect()
    # Subscribed messages will be delivered to this callback
    mqtt.set_callback(evalute_message)
    mqtt.set_last_will(b"led_matrix/status", "offline", qos=1)
    mqtt.connect()
    mqtt.subscribe(TOPIC, qos=1)
    mqtt.subscribe(TOPIC_2, qos=1)
    mqtt.publish(b"led_matrix/status", "online", qos=1)

    while True:
        try:
            # micropython.mem_info()
            print("Connected to %s, subscribed to %s topic" % (SERVER, TOPIC))
            while True:
                mqtt.check_msg()
                mqtt.ping()
                time.sleep(1)
                # print('ping')
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
