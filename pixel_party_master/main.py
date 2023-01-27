import time
import machine
from machine import Pin, RTC, SoftI2C
import ubinascii
import gc
from neopixel import NeoPixel
from random import randint
import json

from ulogging import Logger
from ulogging import DEBUG
from networking import Client, Server
from networking import download_json_file
from networking import LINK, ConnectionError
from umqtt.simple import MQTTClient
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import urequests as requests


class Pixel:
    def __init__(self, id, x, y, color=[255, 0, 255], brightness=0.1):
        self.id = id
        self.color = color
        self.origin_color = color
        self.brightness = brightness
        self.x = x
        self.y = y
        self.origin_x = x
        self.origin_y = y
        self._calculate_brightness()
        self.in_field_of_view = True

    def _calculate_brightness(self):
        calculated_color = []
        for value in self.origin_color:
            value = int(value * self.brightness)
            calculated_color.append(value)
        self.color = calculated_color

    def change_brightness(self, brightness):
        calculated_color = []
        for value in self.origin_color:
            value = int(value * brightness)
            calculated_color.append(value)
        self.color = calculated_color


class Sprite:
    def __init__(self, name, pixels_file_path, x=0, y=0):
        self.id = id(self)
        self.name = name
        self.pixels_file_path = pixels_file_path
        self.x = x
        self.y = y
        self.pixels = [
                        Pixel(self.id, 0, 0),
                      ]
        self.load_pixels_file()
        self.set_pos(self.x, self.y)

    def add_pixels(self, int_array):
        self.pixels = []
        y = 0
        for row in int_array:
            x = 0
            for value in row:
                if value:
                    pixel = Pixel(self.id, x, y)
                    self.pixels.append(pixel)
                x += 1
            y += 1
    
    def add_colored_pixels(self, color_array):
        self.pixels = []
        y = 0
        for row in color_array:
            x = 0
            for value in row:
                if value:
                    pixel = Pixel(self.id, x, y, color=color_array[y][x])
                    gc.collect()
                    self.pixels.append(pixel)
                x += 1
            y += 1
        gc.collect()
        
    def _read_pixels_from_file(self, filename):
        file = open(filename)
        row = []
        color_array = []
        for line in file:
            row = line.split(';')
            del row[-1]
            new_row = []
            for value in row:
                rgb_list = []
                value_list = value[1:-1].split(',')
                for rgb_value in value_list:
                    rgb_list.append(int(rgb_value))
                    gc.collect()
                new_row.append(rgb_list)
            color_array.append(new_row)
        file.close()
        self.add_colored_pixels(color_array)

    def load_pixels_file(self):
        self._read_pixels_from_file(f'{self.pixels_file_path}')
        
    # def deinit_pixels_file(self):
    #     self.pixels.clear()

    def read_pixels_from_broker(self, data):
        data_lines = data.split('\n')
        row = []
        color_array = []
        for line in data_lines:
            gc.collect()
            row = line.split(';')
            del row[-1]
            new_row = []
            for value in row:
                rgb_list = []
                value_list = value[1:-1].split(',')
                for rgb_value in value_list:
                    rgb_list.append(int(rgb_value))
                new_row.append(rgb_list)
            color_array.append(new_row)
        gc.collect()
        self.add_colored_pixels(color_array)
    
    def change_all_color(self, new_color):
        pixel_list = self.pixels
        self.pixels = []
        for pixel in pixel_list:
            if pixel.color == [0, 0, 0]:
                self.pixels.append(pixel)
            else:
                pixel.color = new_color
                self.pixels.append(pixel)
    
    def set_pos(self, x, y):
        for pixel in self.pixels:
            pixel.x = pixel.origin_x + x
            pixel.y = pixel.origin_y + y
        
    def move(self, x, y):
        self.x = x
        self.y = y
        for pixel in self.pixels:
            pixel.x = pixel.x + self.x
            pixel.y = pixel.y + self.y

    def change_brightness(self, brightness):
        for pixel in self.pixels:
            pixel.change_brightness(brightness)


class SpriteGroup:
    def __init__(self, sprite_list=[]):
        self.sprites_list = sprite_list
        
    def add(self, sprite):
        self.sprites_list.append(sprite)

    def move(self, x, y):
        for sprite in self.sprites_list:
            sprite.move(x, y)
        
    def remove(self):
        self.sprites.pop()


class Matrix:
    def __init__(self, neopixel, sprites=[], width=16, height=16):
        self.sprites = sprites
        self.width = width
        self.height = height
        self.led_qty = width * height
        self.np = neopixel
        self.coord = self._create_pixel_num_array()
        
    def _create_pixel_num_array(self):
      pixel_num_array = []
      row_start = 0
      row_end = self.height
      for row in range(self.width):
          row = []
          for i in range(row_start, row_end):
            row.append(i)
      
          row_start = row_end
          row_end = row_end + 16
          pixel_num_array.append(row)
          
      count = 0
      for row in pixel_num_array:
          if count % 2 == 0:
              row.reverse()
          count += 1
      
      return pixel_num_array    
    
    def _add_sprite(self, sprite):
        for pixel in sprite.pixels:
            if pixel.x > self.width or pixel.x < 0:
                pixel.in_field_of_view = False
            elif pixel.y > self.height or pixel.y < 0:
                pixel.in_field_of_view = False
            else:
                pixel.in_field_of_view = True
            try:
                if pixel.in_field_of_view:
                    self.np[self.coord[pixel.y][pixel.x]] = pixel.color
                else:
                    self.np[self.coord[pixel.y][pixel.x]] = [0, 0, 0]
            except IndexError:
                pass

    def load_into_np_array(self):
        for sprite in self.sprites:
            self._add_sprite(sprite)

    def show(self):
        self.np.write()

    def delete_sprites(self):
        self.sprites.clear()
        gc.collect()
        
    def clear(self):
        self.np.fill((0, 0, 0))
        self.np.write()
        
    def fill_black(self):
        self.np.fill((0, 0, 0))


class Animation:
    def __init__(self, pin, width=16, height=16):
        self.width = width
        self.height = height
        self.pin = pin
        self.np = NeoPixel(self.pin, width*height)
        self.tick = 0.1

    def _clear(self):
        self.np.fill((0, 0, 0))
        self.np.write()

    def line_top_bottom(self, color=(25, 25, 25)):
        pos = 0
        row = self.height
        while pos < 256:
            while pos < row:
                self.np[pos] = color
                pos = pos + 1
            self.np.write()
            time.sleep(0.05)
            row = row + 16
            self._clear()


    def full_color(self, color):
        self.np.fill(color)
        self.np.write()


    def full_fade_in(self):
        for brightness in range (0, 100):
            self.np.fill((brightness, 0, 0))
            self.np.write()
            time.sleep(0.01)
            
    def color_change(self):
        for red in range (0, 100):
            self.np.fill((red, 0, 0))
            self.np.write()
            time.sleep(0.005)
        red = 100
        for green in range (0, 100):
            self.np.fill((red, green, 0))
            self.np.write()
            time.sleep(0.05)
            red = red - 1
        green = 100
        for blue in range (0, 100):
            self.np.fill((0, green, blue))
            self.np.write()
            time.sleep(0.05)
            green = green - 1

    def random_colors(self):
        for pos in range(0, 256):
            max = randint(0, 50)
            self.np[pos] = (randint(0, max), randint(0, max), randint(0, max))
        self.np.write()

    def random_color_flash(self):
        self.np[randint(0, 255)] = (255, 255, 255)
        self.np[randint(0, 255)] = (255, 0, 0)
        self.np[randint(0, 255)] = (0, 255, 0)
        self.np[randint(0, 255)] = (0, 0, 255)
        self.np[randint(0, 255)] = (255, 0, 255)
        self.np[randint(0, 255)] = (0, 255, 255)
        self.np.write()
        time.sleep(0.03)
        self._clear()


class PixelParty:
    def __init__(self, matrix, pin):
        self.pin = pin
        self.matrix = matrix
        self.tick = 0.1
        self.rtc = RTC()
        self.animation = Animation(pin)
        self.modis = []

    def _reset_matrix(self):
        self.matrix.clear()
        self.matrix.delete_sprite_groups()
        gc.collect()

    def show_picture(self, filename):
        self._reset_matrix()
        sprite = Sprite()
        sprite.read_pixels_from_file(filename)
        spriteGroup = SpriteGroup(sprite_list=[sprite])
        self.matrix.sprite_groups = [spriteGroup.sprites_list]
        self.matrix.show()
        gc.collect()

    def show_picture_2(self, data):
        # self._reset_matrix()
        sprite = Sprite()
        sprite.read_pixels_from_broker(data)
        spriteGroup = SpriteGroup(sprite_list=[sprite])
        self.matrix.sprite_groups = [spriteGroup.sprites_list]
        self.matrix.show()

    def show_picture_3(self, filename):
        # self._reset_matrix()
        sprite = Sprite()
        sprite.read_pixels_from_file(filename)
        spriteGroup = SpriteGroup(sprite_list=[sprite])
        self.matrix.sprite_groups = [spriteGroup.sprites_list]
        self.matrix.show()
        gc.collect()
        
    def show_all_signs(self):
        self._reset_matrix()
        signs = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        sprite = Sprite()
        spriteGroup = SpriteGroup(sprite_list=[sprite])
        self.matrix.sprite_groups = [spriteGroup.sprites_list]
        for sign in signs:
            sprite.read_pixels_from_file('pixels_data/' + sign + '.pixels')
            sprite.change_all_color((100, 0, 0))
            self.matrix.show()
            time.sleep(self.tick)
        gc.collect()

    # def show_time(self):
    #     hour = self.rtc.datetime()[4]
    #     minute = self.rtc.datetime()[5]
    #     second = self.rtc.datetime()[6]
    #     print(hour, minute, second)
    #     time_now = [hour, minute, second]
    #     for num in time_now:
    #         sprite = Sprite()
    #         print('pixels_data/' + str(num) + '.pixels')
    #         sprite.read_pixels_from_file('pixels_data/' + str(num) + '.pixels')
    #         sprite.set_pos(x, 0)
    #         spriteGroup.add(sprite)
    #         x += 6

    def show_text(self, text):
        self._reset_matrix()
        spriteGroup = SpriteGroup(sprite_list=[])
        x = 0
        for letter in text:
            sprite = Sprite()
            sprite.read_pixels_from_file('pixels_data/' + letter + '.pixels')
            sprite.set_pos(x, 0)
            spriteGroup.add(sprite)
            x += 6

        shift = 0
        spriteGroup.move(16, 0)
        while shift < (len(text)*5+20):
            self.matrix.sprite_groups = [spriteGroup.sprites_list]
            self.matrix.show()
            time.sleep(0.1)
            spriteGroup.move(-1, 0)
            shift += 1
        gc.collect()

    def show_all_animations(self):
        self.animation.line_top_bottom()
        # animation.full_fade_in()
        self.animation.color_change()
        # animation.full_color()
        rounds = 0
        while rounds < 100:
            self.animation.random_color_flash()
            rounds += 1
        rounds = 0
        while rounds < 100:
            self.animation.random_colors()
            rounds += 1
        gc.collect()


class Clock:
    def __init__(self, logger):
        self.rtc = RTC()
        self.logger = logger
        self.client = Client(logger)

    def _set_rtc_by_internet(self):
        data = download_json_file(LINK['datetime'])
        self.rtc.datetime((
            data['year'],
            data['month'],
            data['day'],
            0,                  # not implemented yet                 
            data['hour'],
            data['minute'],
            data['seconds'],
            data['milliSeconds']
        ))

    def set_time(self):
        self.logger.info("Try to get the time-signal by internet")
        self.client.activate()
        self.client.search_wlan()
        self.client.connect()
        # networking.print_ip_infos()
        self._set_rtc_by_internet()
        self.client.disconnect()
        self.client.deactivate()


class Weather:
    def __init__(self, base_url, owm_key, owm_lat, owm_lon, owm_units, owm_lang):
        self.base_url = base_url
        self.owm_key = owm_key
        self.owm_lat = owm_lat
        self.owm_lon = owm_lon
        self.owm_units = owm_units
        self.owm_lang = owm_lang
        self.weather_data = None

    def get_current_weather(self):
        lat = "&lat=" + self.owm_lat 
        lon = "&lon=" + self.owm_lon
        key = "&appid=" + self.owm_key
        units = "&units=" + self.owm_units
        lang = "&lang=" + self.owm_lang

        url = self.base_url + lat + lon + key + units + lang
        res = requests.get(url)
        self.weather_data = json.loads(res.text)

    def get_weather_icon_name(self):
        weather_data = self.weather_data['weather'][0]
        folder = 'pixels_data/'
        
        if weather_data['icon'] == '01d':
            return folder + 'sun.pixels'
        elif weather_data['icon'] == '01n':
            return folder +  'moon.pixels'
        elif weather_data['icon'] == '02d':
            return folder +  'cloud.pixels'
        elif weather_data['icon'] == '02n':
            return folder +  'cloud.pixels'
        elif weather_data['icon'] == '03d':
            return folder +  'cloud.pixels'
        elif weather_data['icon'] == '03n':
            return folder +  'cloud.pixels'
        elif weather_data['icon'] == '04d':
            return folder +  'cloud.pixels'
        elif weather_data['icon'] == '04n':
            return folder +  'cloud.pixels'
        elif weather_data['icon'] == '09d':
            return folder +  'rain.pixels'
        elif weather_data['icon'] == '09n':
            return folder +  'rain.pixels'
        elif weather_data['icon'] == '10d':
            return folder +  'rain.pixels'
        elif weather_data['icon'] == '10n':
            return folder +  'rain.pixels'
        elif weather_data['icon'] == '11d':
            return folder +  'lightning.pixels'
        elif weather_data['icon'] == '11n':
            return folder +  'lightning.pixels'
        elif weather_data['icon'] == '13d':
            return folder +  'snow.pixels'
        elif weather_data['icon'] == '13n':
            return folder +  'snow.pixels'


class Button:
    def __init__(self, name, pin_num):
        self.name = name
        self.pin_num = pin_num


class Buttons:
    def __init__(self, buttons={}):
        self.buttons = buttons

    def add_button(self, button):
        self.buttons[button.name] = Pin(int(button.pin_num), Pin.IN)

    def add_buttons(self, buttons):
        for button in buttons:
            self.buttons[button.name] = button.pin

    def get_all_states(self):
        output = {}
        for name, pin in self.buttons.items():
            output[name] = pin.value()
        return output

    def get_state_of(self, name):
        return self.buttons[name].value()


class Connector:
    def __init__(self, logger, lcd, client, server, mqtt, fallback_btn, subscribed_topics):
        self.logger = logger
        self.lcd = lcd
        self.client = client
        self.server = server
        self.mqtt = mqtt
        self.fallback_btn = fallback_btn
        self.subscribed_topics = subscribed_topics
        self.wlan_reconnect_timer = machine.Timer(0)
        self.mqtt_listener_timer = machine.Timer(1)
        self.mqtt_ping_timer = machine.Timer(2)
        self._init_mqtt()

    def _init_mqtt(self):
        self.mqtt.set_callback(self._evaluate_mqtt_msg)
        self.mqtt.set_last_will(b"led_matrix/status", "offline", qos=1)

    def _evaluate_mqtt_msg(self, topic, msg):
        topic = topic.decode('utf-8')
        msg = msg.decode('utf-8')
        self.logger.debug(topic + ' ' + msg)

    def connect_wlan(self):
        self.client.activate()
        # self.client.read_stored_networks()
        connected = self.client.connect()
        if connected:
            write_to_lcd(self.lcd, 'Connected to', self.client.connected_network)
        else:
            write_to_lcd(self.lcd, 'Not connected', 'to Access Point')

    def disconnect_wlan(self):
        try:
            self.client.disconnect()
        except TypeError:
            self.logger.debug('No Access Point is connected')
        self.client.deactivate()

    def _reconnect(self):
        if not self.client.wlan.isconnected():
            self.logger.info('Reconnecting to Access Point...')
            self.client.wlan.active(False)
            self.client.wlan.active(True)
            self.connect_wlan()

    def connect_mqtt(self):
        self.mqtt.connect()
        self.logger.info('Connected to MQTT Broker')
        for topic in self.subscribed_topics:
            self.mqtt.subscribe(topic, qos=1)
        self.mqtt.publish(b"led_matrix/status", "online", qos=1)
        self.activate_mqtt_listener_timer()
        self.activate_mqtt_ping_timer()

    def disconnect_mqtt(self):
        self.deactivate_mqtt_listener_timer()
        self.deactivate_mqtt_ping_timer()
        try:
            self.mqtt.disconnect()
        except OSError as error:
            self.logger.warning('Not connected to MQTT Broker: ' + str(error))
        except AttributeError:
            pass
        self.logger.info('Disconnected from MQTT Broker')

    def activate_reconnect_timer(self, sleep_time=20):
        self.wlan_reconnect_timer.init(period=sleep_time*1000, mode=machine.Timer.PERIODIC, callback=lambda t: self._reconnect())

    def deactivate_reconnect_timer(self):
        self.wlan_reconnect_timer.deinit()

    def _mqtt_check_msg(self):
        try:
            self.mqtt.check_msg()
        except OSError as error:
            self.logger.warning('Lost connection to MQTT Broker: ' + str(error))
            self.logger.debug('Deactivate mqtt listener and ping timer')
            self.deactivate_mqtt_listener_timer()
            self.deactivate_mqtt_ping_timer()

    def activate_mqtt_listener_timer(self):
        self.mqtt_listener_timer.init(period=100, mode=machine.Timer.PERIODIC, callback=lambda t: self._mqtt_check_msg())

    def deactivate_mqtt_listener_timer(self):
        self.mqtt_listener_timer.deinit()

    def _mqtt_ping(self):
        try:
            self.mqtt.ping()
        except OSError as error:
            self.logger.warning('Lost connection to MQTT Broker: ' + str(error))
            self.logger.debug('Deactivate mqtt listener and ping timer')
            self.deactivate_mqtt_listener_timer()
            self.deactivate_mqtt_ping_timer()

    def activate_mqtt_ping_timer(self):
        self.mqtt_ping_timer.init(period=9000, mode=machine.Timer.PERIODIC, callback=lambda t: self._mqtt_ping())

    def deactivate_mqtt_ping_timer(self):
        self.mqtt_ping_timer.deinit()

    def start(self):
        self.connect_wlan()
        if self.client.wlan.isconnected():
            self.logger.info(f'Connect to MQTT Broker {self.mqtt.server}')
            try:
                self.connect_mqtt()
            except OSError as error:
                self.logger.warning('MQTT Connect Problem: ' + str(error))
                self.logger.warning('Could not connect to MQTT Broker.')
                self.logger.warning('Maybe the Broker is not reachable or the IP is wrong?')
        else:
            self.logger.info('Not connected to MQTT Broker')


class StaticPage:
    def __init__(self, name):
        self.name = name
        # data_structure for self.screen_objects
        # [{'pixels_file': 'test', 'coord' : {'x': 10, 'y': 12}},
        #  {'pixels_file': 'test_2', 'coord' : {'x': 42, 'y': 24}}]
        self.screen_objects = []
        self.sprites = []
        self.display_time = None

    def _create_word(self):
        pass

    def _load_sprite_names(self):
        # load sprite names from a "self.name".static-file 
        # to load it in self.screen_objects
        with open(f'/static_pages_data/{self.name}.static') as file:
            for line in file:
                line = line.split(';')
                if line[0] == 'display_time':
                    self.display_time = int(line[1])
                else:
                    x_y = line[1].split('|')
                    x = x_y[0].replace('\r\n', '')
                    y = x_y[1].replace('\r\n', '')
                    screen_type = line[2].replace('\r\n', '')
                    size = line[3].replace('\r\n', '')
                    screen_obj = {
                        'pixels_file': line[0],
                        'coord': {'x': x, 'y': y},
                        'screen_type': screen_type,
                        'size': size}
                    self.screen_objects.append(screen_obj)

    def add_sprite(self, name, x, y):
        pass

    def save_sprite_names(self):
        pass
        # write sprite names from self.screen_objects into a "self.name".static-file
        # if self.screen_objects is Empty then dont allow to save because you eventually
        # override existing data!
        # you can reload it later from file system

    def _create_sprite_path(self, screen_type):
        if screen_type == 'pic':
            return '/pixels_data/pictures'
        elif screen_type == 'txt':
            return '/pixels_data/texts'

    def load_sprites(self):
        self._load_sprite_names()
        # before i have sprites in self.sprites
        # i have to find it with the data in self.screen_objects
        for obj in self.screen_objects:
            try:
                # TESTS IT!!
                # an das sprtie objekt den richtigen pfad mitteile anhand des screen_type pfad erzeugen!
                directory = self._create_sprite_path(obj['screen_type'])
                path = f'{directory}/{obj["pixels_file"]}-{obj["size"]}.pixels'
                new_sprite = Sprite(obj["pixels_file"], path, x=int(obj['coord']['x']), y=int(obj['coord']['y']))
                self.sprites.append(new_sprite)
            except OSError as error:
                print(f'Problem with {obj}: {error}')
                print('It should request the other mqtt client for the file')
                # then try again
                # self._read_pixels_from_file(f'{self.name}.pixels')

    def clear_sprites(self):
        self.sprites.clear()
        gc.collect()



class Display:
    pass

class Modus:
    pass

class LCD:
    pass

class ConfigParser:
    def __init__(self):
        self.data = {}

    def read(self, file_path):
        current_section = None
        with open(file_path, 'r') as file:
            for line in file:
                if '[' in line:
                    line = line.replace('[', '').replace(']', '')
                    current_section = line.replace('\r\n', '')
                    self.data[current_section] = {}
                else:
                    if line in ['\n', '\r\n']:
                        pass
                    else:
                        key_and_value = line.split('=')
                        key = key_and_value[0]
                        value = key_and_value[1].replace('\r\n', '')
                        self.data[current_section][key] = value

    def write(self, file_path):
        with open(file_path, 'w') as file:
            for key, value in self.data.items():
                file.write(f'[{key}]\r\n')
                for key_2, value_2 in value.items():
                    file.write(f'{key_2}={value_2}\r\n')
                file.write('\n')

    def search_seaction_for_key(self, searched_key):
        for section_name, section_data in self.data.items():
            for key in section_data.keys():
                if searched_key == key:
                    return section_name
        return None



def write_to_lcd(lcd, line_1, line_2):
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr(line_1)
    lcd.move_to(0, 1)
    lcd.putstr(line_2)


def evaluate_message(topic, msg):
    topic = topic.decode('utf-8')
    msg = msg.decode('utf-8')
    print(topic, msg)
    
    if topic == 'website_connector/command':
        print('restart master')
        if msg == 'restart':
            machine.reset()
    elif topic == 'mqtt_connector/modus':
        print('Modus: ', msg)
    elif topic == "website_connector/modus/text/data":
        print('text: ', msg)
        MODIS.clear()
        MODIS.append({'text': msg})
    elif topic == "website_connector/modus/animation/data":
        print('animation: ', msg)
        MODIS.clear()
        MODIS.append({'animation': msg})
    elif topic == "website_connector/modus/picture/data":
        print('picture: ', msg)
        MODIS.clear()
        MODIS.append({'picture': msg})
    elif topic == "website_connector/modus/weather/data":
        print('weather: ', msg)
        MODIS.clear()
        MODIS.append({'weather': msg})


def load_static_page(static_page_name, matrix, logger):
    logger.debug(f'Load static page {static_page_name}')
    page = StaticPage(static_page_name)
    page.load_sprites()
    logger.info(f'Display time of {static_page_name}: {page.display_time}')
    for sprite in page.sprites:
        matrix.sprites.append(sprite)
        logger.debug(f'Load Sprite {sprite.name} on position {sprite.x}|{sprite.y}')
    matrix.load_into_np_array()
    gc.collect()


class Page:
    def __init__(self):
        self.display_time = None

    def load_into_matrix(self):
        pass



def main():
    config = ConfigParser()
    config.read('master_data.config')

    buttons = Buttons()
    for name, pin in config.data['buttons'].items():
        buttons.add_button(Button(name, pin))
    i2c = SoftI2C(
        scl=Pin(int(config.data['lcd']['scl_pin'])),
        sda=Pin(int(config.data['lcd']['sda_pin'])),
        freq=10000)
    lcd = I2cLcd(
        i2c,
        int(config.data['lcd']['i2c_addr']),
        int(config.data['lcd']['total_rows']), 
        int(config.data['lcd']['total_columns']))
    logger = Logger(log_level=DEBUG)
    client = Client(logger)
    client.add_config_networks(config.data['network'])
    server = Server(logger)
    mqtt = MQTTClient(
        config.data['mqtt']['client_id'], 
        config.data['mqtt']['broker_ip'], 
        user=config.data['mqtt']['user'], 
        password=config.data['mqtt']['password'], 
        port=1884, 
        keepalive=10)
    connector = Connector(
        logger,
        lcd,
        client,
        server,
        mqtt,
        buttons.buttons['fallback'],
        [b"led_matrix/#", b"website_connector/#"])
    led_qty = int(config.data['matrix']['width']) * int(config.data['matrix']['height'])
    matrix_pin = Pin(int(config.data['matrix']['gpio_pin']), Pin.OUT)
    neopixel = NeoPixel(matrix_pin, led_qty)
    matrix = Matrix(neopixel)
    # pixelParty = PixelParty(matrix, matrix_pin)
    # weather = Weather(
    #     config.data['weather']['base_url'],
    #     config.data['weather']['owm_key'],
    #     config.data['weather']['owm_lat'],
    #     config.data['weather']['owm_lon'],
    #     config.data['weather']['owm_units'],
    #     config.data['weather']['owm_lang'])

    print('Start Pixel Party Master')
    print('Read Configuration File')
    write_to_lcd(lcd, "Start Pixel", "Party Master")
    connector.start()
    # weather.get_current_weather()
    # ther_data['weather'][0].items():
    #     print(key, ': ',vaprint('current weather: ')
    # for key, value in weather.wealue)

    load_static_page('test_2', matrix, logger)

    try:
        while True:
            # check all buttons
            if buttons.buttons['fallback'].value():
                connector.disconnect_mqtt()
                connector.disconnect_wlan()
                server.activate()
                server.wait_for_connection()
                data = server.receive_http_data(config.data)
                logger.debug(data)
                for key, value in data.items():
                    config.data[config.search_seaction_for_key(key)][key] = value
                config.write('master_data.config')
                machine.reset()
            
            # display things on led matrix
            matrix.show()
    except KeyboardInterrupt:
        matrix.clear()
        matrix.delete_sprites()

    # try:
    #     while True:
    #         for item in MODIS:
    #             for modus, data in item.items():
    #                 if modus == 'text':
    #                     pixelParty.show_text(data)
    #                 elif modus == 'animation':
    #                     if data == 'a':
    #                         pixelParty.animation.line_top_bottom()
    #                     elif data == 'b':
    #                         pixelParty.animation.full_color((100, 100, 100))
    #                     # elif data == 'c':
    #                     #      pixelParty.animation.full_fade_in()
    #                     elif data == 'd':
    #                         pixelParty.animation.color_change()
    #                     elif data == 'e':
    #                         pixelParty.animation.random_colors()
    #                     elif data == 'f':
    #                         pixelParty.animation.random_color_flash()
    #                 elif modus == 'picture':
    #                     try:
    #                         pixelParty.show_picture_2(data)
    #                         time.sleep(1)
    #                     except MemoryError:
    #                         gc.collect()
    #                 elif modus == 'weather':
    #                     try:
    #                         pixelParty.show_picture_3(weather.get_weather_icon_name())
    #                         time.sleep(1)
    #                     except MemoryError:
    #                         gc.collect()
    # except KeyboardInterrupt:
    #     pixelParty.matrix.clear()
    #     pixelParty.matrix.delete_sprite_groups()

if __name__ == '__main__':
    main()
