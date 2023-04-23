from umqtt.simple import MQTTClient
from machine import Pin
import time
from neopixel import NeoPixel
from random import randint

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
MATRIX_PIN = 33
ANI_CONFIGS = 'ani_configs'

PIN = Pin(MATRIX_PIN, Pin.OUT)
NP = NeoPixel(PIN, 1024)


mqtt = MQTTClient(CLIENT_ID, SERVER, user=USER, password=PASSWORD, port=1884, keepalive=10)


class Matrix:
    def __init__(self, np):
        self.np = np

    def read_pixels_from_file(self, filename):
        pixels = []
        with open(f'data/{filename}.pixels', 'r') as file:
            for line in file:
                gc.collect()
                line = line.rstrip()
                line = line.split(';')
                del line[-1]
                for pixel in line:
                    pixel = pixel.replace('[', '')
                    pixel = pixel.replace(']', '')
                    pixel = pixel.replace(' ', '')
                    pixel_list = []
                    for value in pixel.split(','):
                        pixel_list.append(int(value))
                    pixels.append(pixel_list)

        for i, pixel in enumerate(pixels):
            self.np[i] = pixels[i]
        self.np.write()
        pixels.clear()
        gc.collect()

    def write_to_led(self, string_list):
        pixels_string = []
        for line in string_list:
            pixels_string.append(line.decode().rstrip())  

        for i, pixel in enumerate(pixels_string):
            rgb_value = []
            pixel = pixel.split(',')
            for value in pixel:
                rgb_value.append(int(value))
            self.np[i] = rgb_value
        self.np.write()

    def clear(self):
        self.np.fill((0, 0, 0))
        self.np.write()


class Animation:
    def __init__(self, np, brightness=10):
        self.np = np
        self.br = brightness
        self.config = AnimationConfig()

    def _clear(self):
        self.np.fill((0, 0, 0))
        self.np.write()

    def show(self):
        if self.config.data['ani_type'] == 'random_color_flash':
            self.random_color_flash(int(self.config.data['sleep_time']))
        elif self.config.data['ani_type'] == 'random_colors':
            self.random_colors()
    
    def random_color_flash(self, sleep_time):
        self.np[randint(0, self.np.n - 1)] = (255, 255, 255)
        self.np[randint(0, self.np.n - 1)] = (255, 0, 0)
        self.np[randint(0, self.np.n - 1)] = (0, 255, 0)
        self.np[randint(0, self.np.n - 1)] = (0, 0, 255)
        self.np[randint(0, self.np.n - 1)] = (255, 0, 255)
        self.np[randint(0, self.np.n - 1)] = (0, 255, 255)
        self.np.write()
        time.sleep_ms(sleep_time)
        self._clear()

    def random_colors(self):
        for pos in range(0, self.np.n - 1):
            max = randint(0, self.br)
            self.np[pos] = (randint(0, max), randint(0, max), randint(0, max))
        self.np.write()

    def color_squares(self, color=[10, 10, 10]):
        for pos in range (116, 123):
            self.np[pos] = color
            self.np[pos + 17] = color
            self.np[pos + 32] = color
            self.np[pos + 49] = color
            self.np[pos + 64] = color
            self.np[pos + 81] = color
            self.np[pos + 96] = color

            self.np[pos + 256] = color
            self.np[pos + 17 + 256] = color
            self.np[pos + 32 + 256] = color
            self.np[pos + 49 + 256] = color
            self.np[pos + 64 + 256] = color
            self.np[pos + 81 + 256] = color
            self.np[pos + 96 + 256] = color

            self.np[pos + 256*2] = color
            self.np[pos + 17 + 256*2] = color
            self.np[pos + 32 + 256*2] = color
            self.np[pos + 49 + 256*2] = color
            self.np[pos + 64 + 256*2] = color
            self.np[pos + 81 + 256*2] = color
            self.np[pos + 96 + 256*2] = color

            self.np[pos + 256*3] = color
            self.np[pos + 17 + 256*3] = color
            self.np[pos + 17 + 256*3] = color
            self.np[pos + 32 + 256*3] = color
            self.np[pos + 49 + 256*3] = color
            self.np[pos + 64 + 256*3] = color
            self.np[pos + 81 + 256*3] = color
            self.np[pos + 96 + 256*3] = color
        self.np.write()

    def single_color_square(self, num, color=[10, 10, 10]):
        for pos in range (116, 123):
            self.np[pos + 256*num] = color
            self.np[pos + 17 + 256*num] = color
            self.np[pos + 32 + 256*num] = color
            self.np[pos + 49 + 256*num] = color
            self.np[pos + 64 + 256*num] = color
            self.np[pos + 81 + 256*num] = color
            self.np[pos + 96 + 256*num] = color 
        self.np.write()

    def completely_fade_in(self, color=[1, 1, 1], step_dura=10):
        for br in range(50):
            self.np.fill([color[0]*br, color[1]*br, color[2]*br])
            time.sleep_ms(step_dura)
            self.np.write()

    def lightning(self, on_time=10):
        self.np.fill((100, 100, 100))
        self.np.write()
        time.sleep_ms(on_time)
        self.np.fill([0, 0, 0])
        self.np.write()

    def single_mat_fade_in(self, num, color=[1, 1, 1], step_dura=10):
        for br in range(50):
            for pos in range((num-1)*256, 256 * num):
                self.np[pos] = [color[0]*br, color[1]*br, color[2]*br]
            self.np.write()
            time.sleep_ms(step_dura)

    def right_line(self, mat_num=3, color=[10, 10, 10]):
        for i in range(8):
            if i % 2 == 0:
                self.np[256*mat_num + 32*i + 31] = color
                self.np[256*mat_num + 32*i + 63] = color
            self.np[256*mat_num + 32*i] = color
        self.np.write()

    def destroyed_right_line(self, mat_num=3, color=[10, 10, 10]):
        for i in range(8):
            if i % 2 == 0:
                self.np[256*mat_num + 32*i + 30] = color
                self.np[256*mat_num + 32*i + 61] = color
            self.np[256*mat_num + 32*i] = color
        self.np.write()

    def unfilled_square(self, color=[10, 10, 10]):
        # right line
        mat_num = 1
        for i in range(8):
            if i % 2 == 0:
                self.np[256*mat_num + 32*i + 31] = color
                self.np[256*mat_num + 32*i + 63] = color
            self.np[256*mat_num + 32*i] = color
        mat_num = 3
        for i in range(8):
            if i % 2 == 0:
                self.np[256*mat_num + 32*i + 31] = color
                self.np[256*mat_num + 32*i + 63] = color
            self.np[256*mat_num + 32*i] = color
        

        # left line
        mat_num = 1
        color = [10, 0, 0]
        for i in range(8):
            if i % 2 == 0:
                self.np[250*mat_num + 32*i + 31] = color
                self.np[250*mat_num + 32*i + 63] = color
            self.np[250*mat_num + 32*i] = color

        # top line
        # bottom line

        self.np.write()


class AnimationConfig:
    def __init__(self):
        self.data = {}
        self.config_folder = ANI_CONFIGS

    def read(self, filename):
        with open(f'{self.config_folder}/{filename}.ani', 'r') as file:
            for line in file:
                items = line.split('=')
                self.data[items[0]] = items[1].replace('\n', '')

    def write(self, filename):
        with open(f'{self.config_folder}/{filename}.ani', 'x') as file:
            for key, value in self.data.items():
                file.write(f'{key}={value}\n')


# Animation Sequences
def color_squares_5_times(animation, break_time=80):
    animation.color_squares(color=[10, 0, 0])
    time.sleep_ms(break_time)
    animation.color_squares(color=[0, 10, 0])
    time.sleep_ms(break_time)
    animation.color_squares(color=[0, 0, 10])
    time.sleep_ms(break_time)
    animation.color_squares(color=[10, 0, 0])
    time.sleep_ms(break_time)
    animation.color_squares(color=[0, 10, 0])


def single_squares_5_times(animation, break_time=80):
    animation.single_color_square(0)
    time.sleep_ms(break_time)
    animation._clear()
    animation.single_color_square(1)
    time.sleep_ms(break_time)
    animation._clear()
    animation.single_color_square(3)
    time.sleep_ms(break_time)
    animation._clear()
    animation.single_color_square(2)
    time.sleep_ms(break_time)
    animation._clear()
    animation.single_color_square(0)
    time.sleep_ms(break_time)
    animation._clear()


def strobes(animation, qty, break_time=10):
    num = 0
    while True:
        if num >= qty:
            break
        animation.lightning()
        time.sleep_ms(break_time)
        num = num + 1


def mat_single_fade_in(animation):
    animation.single_mat_fade_in(1)
    animation._clear()
    animation.single_mat_fade_in(2)
    animation._clear()
    animation.single_mat_fade_in(3)
    animation._clear()
    animation.single_mat_fade_in(4)
    animation._clear()


def wriggling_right_line(animation, qty):
    num = 0
    while True:
        if num == qty:
            break
        animation.right_line(color=[10, 10, 20])
        #animation.right_line(mat_num=1, color=[10, 10, 20])
        time.sleep_ms(1)
        animation._clear()
        animation.destroyed_right_line(color=[255, 255, 255])
        #animation.destroyed_right_line(mat_num=1, color=[255, 255, 255])
        animation._clear()
        num = num + 1


def start_animation():
    animation = Animation(NP)

    try:
        color_squares_5_times(animation)
        single_squares_5_times(animation)
        animation.completely_fade_in()
        strobes(animation, 5)
        mat_single_fade_in(animation)
        wriggling_right_line(animation, 5)
        # animation.unfilled_square()

    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        print("Clear Screen")
        animation._clear()


def evaluate_message(topic, msg):
    topic = topic.decode('utf-8')
    msg = msg.decode('utf-8')
    print(topic, msg)
    
    if topic == f'{COMPUTER_ID}/music':
        print("Start Animation for", f'"{msg}"')
        start_animation()


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
            mqtt.set_callback(evaluate_message)
            mqtt.set_last_will(b"led_matrix/status", "offline", qos=1)
            mqtt.connect()
            mqtt.subscribe(TOPIC, qos=1)
            mqtt.subscribe(TOPIC_2, qos=1)
            mqtt.publish(b"led_matrix/status", "online", qos=1)
            # client.disconnect()
            # client.deactivate()
        

if __name__ == '__main__':
    main()
