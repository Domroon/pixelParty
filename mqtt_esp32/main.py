from umqtt.simple import MQTTClient
from machine import Pin
import ubinascii
import machine
import micropython

from ulogging import Logger
from networking import Client


# ESP8266 ESP-12 modules have blue, active-low LED on GPIO2, replace
# with something else if needed.
led = Pin(2, Pin.OUT, value=1)

# Default MQTT server to connect to
SERVER = "192.168.144.168"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
TOPIC = b"led"


state = 0


def sub_cb(topic, msg):
    global state
    print((topic, msg))
    if msg == b"on":
        led.value(0)
        state = 1
        print("LED ist AN")
    elif msg == b"off":
        led.value(1)
        state = 0
        print("LED ist AUS")
    elif msg == b"toggle":
        # LED is inversed, so setting it to current state
        # value will make it toggle
        led.value(state)
        state = 1 - state


def main(server=SERVER):
    logger = Logger()
    client = Client(logger)
    client.activate()
    client.search_wlan()
    client.connect()
    c = MQTTClient(CLIENT_ID, server, port=1884, keepalive=30)
    # Subscribed messages will be delivered to this callback
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(TOPIC)
    print("Connected to %s, subscribed to %s topic" % (server, TOPIC))

    try:
        while 1:
            # micropython.mem_info()
            c.wait_msg()
    finally:
        c.disconnect()
        client.disconnect()
        client.deactivate()
        

if __name__ == '__main__':
    main()
