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
SERVER = "192.168.188.168"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
TOPIC = b"led_matrix"


def evalute_message(topic, msg):
    print((topic, msg))
    if msg == b"restart":
        print('Restart Matrix ESP')
        pin_g2.value(1)
        time.sleep(0.1)
        pin_g2.value(0)


def main(server=SERVER):    
    logger = Logger()
    client = Client(logger)
    client.activate()
    client.search_wlan()
    client.connect()
    mqtt = MQTTClient(CLIENT_ID, server, port=1884, keepalive=30)
    # Subscribed messages will be delivered to this callback
    mqtt.set_callback(evalute_message)
    mqtt.connect()
    mqtt.subscribe(TOPIC)
    print("Connected to %s, subscribed to %s topic" % (server, TOPIC))

    try:
        while 1:
            # micropython.mem_info()
            mqtt.wait_msg()
    finally:
        mqtt.disconnect()
        client.disconnect()
        client.deactivate()
        

if __name__ == '__main__':
    main()
