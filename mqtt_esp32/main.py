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
SERVER = "192.168.128.168"
CLIENT_ID = b"matrix-" + ubinascii.hexlify(machine.unique_id())
TOPIC = b"led_matrix/#"
TOPIC_2 = b"website_connector/#"
USER = 'domroon'
PASSWORD = 'MPCkY5DGuU19sGgpvQvgYqN8Uw0'

mqtt = MQTTClient(CLIENT_ID, SERVER, user=USER, password=PASSWORD, port=1884, keepalive=10)


def evaluate_message(topic, msg):
    topic = topic.decode('utf-8')
    msg = msg.decode('utf-8')
    print(topic, msg)
    
    if topic == 'website_connector/command':
        print('restart master')
        if msg == 'restart':
            pin_g2.value(1)
            time.sleep(0.2)
            pin_g2.value(0)
    elif topic == 'mqtt_connector/modus':
        print('Modus: ', msg)
    elif topic == "website_connector/modus/text/data":
        print('text: ', msg)
        print(f'Sending Text Data ("{msg}") via SPI to Master')
        
        # init spi bus
        MOSI = Pin(23)
        MISO = Pin(19)
        SCK = Pin(18)
        chip_select = Pin(5, mode=Pin.OUT, value=1)

        spi = SoftSPI(mosi=MOSI, miso=MISO, sck=SCK)
        spi.init()
        
        # send each byte from the bytearray(payload) in a for-loop
        payload = bytearray(msg)
        chip_select.value(0)  # start communication
        print('chip_select: ', chip_select.value())
        time.sleep(1)
        # spi.write(payload)
        spi.write(b'123456')
        chip_select.value(1)  # end communication
        print('chip_select: ', chip_select.value())

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
