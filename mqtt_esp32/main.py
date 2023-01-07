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
SERVER = "192.168.62.168"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
TOPIC = b"led_matrix/#"


def evalute_message(topic, msg):
    print((topic, msg))
    if msg == b"led_matrix/restart":
        print('Restart Matrix ESP')
        pin_g2.value(1)
        time.sleep(0.1)
        pin_g2.value(0)


def main():    
    logger = Logger()
    client = Client(logger)
    client.activate()
    client.search_wlan()
    client.connect()
    mqtt = MQTTClient(CLIENT_ID, SERVER, port=1884, keepalive=10)
    # Subscribed messages will be delivered to this callback
    mqtt.set_callback(evalute_message)
    mqtt.set_last_will(b"led_matrix/status", "offline", qos=1)
    mqtt.connect()
    mqtt.subscribe(TOPIC, qos=1)
    mqtt.publish(b"led_matrix/status", "online", qos=1)

    while True:
        try:
            # micropython.mem_info()
            print("Connected to %s, subscribed to %s topic" % (SERVER, TOPIC))
            while True:
                mqtt.check_msg()
                mqtt.ping()
                time.sleep(1)
                print('ping')
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
