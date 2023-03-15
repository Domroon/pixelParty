import time
import requests
from pathlib import Path
from PIL import Image
from logging import getLogger
from secrets import token_urlsafe
import io

import wiringpi
import RPi.GPIO as GPIO
import paho.mqtt.client as pahoMqtt

# UART
IRQ_PIN = 4
OUTPUT_MODE = 1
BAUDRATE = 115200 

# PATHs
CWD = Path.cwd()
DATA_FOLDER = CWD / 'data'
ANI_CONFIGS = CWD / 'ani_configs'
IMAGE_PATH = CWD / 'pictures'
WORDS_PATH = CWD / 'words'
LETTERS_PATH = CWD / 'letters'
ICONS_PATH = CWD / 'weather_icons'

# MATRIX
MATRIX_COLS = 32
MATRIX_ROWS = 32
PIC_BRIGHTNESS = 10

# APIs
WEATHER_API_KEY = '3a9a45b1d4bcf93686f67e679d86e263'
NEWS_API_KEY = '5db667c899c24686b19f6565c0c63ee3'

# MQTT
USERNAME = "domroon"
PASSWORD = "MPCkY5DGuU19sGgpvQvgYqN8Uw0"
DEVICE_NAME = "pixel-master"
COMPUTER_NAME = "computer-client"


logger = getLogger('mqttInput')
logger.setLevel(pahoMqtt.MQTT_LOG_INFO)


class UARTSender:
    def __init__(self):
        self.ani_conf = AnimationConfig()
        wiringpi.wiringPiSetupGpio()
        wiringpi.pinMode(IRQ_PIN, OUTPUT_MODE)
        self.serial = wiringpi.serialOpen('/dev/ttyS0', BAUDRATE)

    def _send_data(self, data, half):
        counter = 0
        for i, line in enumerate(data):
            if i >= len(data)/2 and half:
                break
            wiringpi.serialPuts(self.serial, line)
            wiringpi.serialPuts(self.serial, '\n')
            print(counter, line)
            counter = counter + 1
            time.sleep(0.000017)
        wiringpi.serialPuts(self.serial, 'EOF')

    def _read_pixels_file(self, filename):
        with open(DATA_FOLDER / filename, 'r') as file:
            pixel_file = file.read()

            pixel_string = pixel_file.replace('\n', '')
            pixel_strings = pixel_string.split(';')
            pixel_strings.pop()
        
        for i in range(len(pixel_strings)):
            pixel_strings[i] = pixel_strings[i].replace('[', '')
            pixel_strings[i] = pixel_strings[i].replace(']', '')
            pixel_strings[i] = pixel_strings[i].replace(' ', '')
        
        return pixel_strings

    def _trigger_irq(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(16, GPIO.OUT)
        GPIO.output(16, 1)
        time.sleep(1)
        GPIO.output(16, 0)
        GPIO.cleanup()

    def send_pixels_data(self, filename, half=False):
        self._trigger_irq()
        time.sleep(0.03)
        wiringpi.serialPuts(self.serial, 'PIXELS')
        wiringpi.serialPuts(self.serial, '\n')
        time.sleep(0.03)
        pixel_strings = self._read_pixels_file(filename)
        self._send_data(pixel_strings, half)

    def send_animation_data(self, filename):
        self._trigger_irq()
        time.sleep(0.03)
        wiringpi.serialPuts(self.serial, 'ANI\n')
        time.sleep(0.03)
        self.ani_conf.read(filename)
        lines=[]
        for key, value in self.ani_conf.data.items():
            lines.append(f'{key}={value}')
        print(lines)
        self._send_data(lines, half=False)

    def set_init_screen(self):
        self._trigger_irq()
        time.sleep(0.03)
        wiringpi.serialPuts(self.serial, 'INIT\n')


class PixelsConverter:
    def __init__(self):
        self.pixels = []
        self.quarters = {}
        self.rearranged_pixels = []

    def _cut_into_quarters(self):
        upper_half = []
        bottom_half = []
        half = int(len(self.pixels) / 2)
        for i in range(0, half):
            upper_half.append(self.pixels[i])

        for i in range(half, int(len(self.pixels))):
            bottom_half.append(self.pixels[i])

        upper_left, upper_right = self._cut_in_half(upper_half)
        bottom_left, bottom_right = self._cut_in_half(bottom_half)
        self.quarters = {
            'upper_left': upper_left,
            'upper_right': upper_right,
            'bottom_left': bottom_left,
            'bottom_right': bottom_right
        }
        
        # reverse every second line
        for pixel_list in self.quarters.values():
            for i, line in enumerate(pixel_list):
                if i % 2 == 0:
                    line.reverse()
    
    def _join_up_quarters(self):
        self.rearranged_pixels.clear()
        for i in range(len(self.quarters['upper_left'])):
            new_line = []
            for value in self.quarters['upper_left'][i]:
                new_line.append(value)
            self.rearranged_pixels.append(new_line)
        
        for i in range(len(self.quarters['upper_right'])):
            new_line = []
            for value in self.quarters['upper_right'][i]:
                new_line.append(value)
            self.rearranged_pixels.append(new_line)

        for i in range(len(self.quarters['bottom_left'])):
            new_line = []
            for value in self.quarters['bottom_left'][i]:
                new_line.append(value)
            self.rearranged_pixels.append(new_line)

        for i in range(len(self.quarters['bottom_right'])):
            new_line = []
            for value in self.quarters['bottom_right'][i]:
                new_line.append(value)
            self.rearranged_pixels.append(new_line)
        
    def _cut_in_half(self, half):
        left_quarter = []
        right_quarter = []
        half_index = int(len(half[0]) / 2)
        for line in half:
            left_quarter.append([line[i] for i in range(half_index)])
            right_quarter.append([line[i] for i in range(half_index, int(len(half[0])))])

        return left_quarter, right_quarter
        
    def _read_pixels_from_file(self, filename):
        self.pixels.clear()
        with open(DATA_FOLDER / filename, 'r') as file:
            for line in file:
                line = line.rstrip()
                line = line.split(';')
                del line[-1]
                line_list = []
                for pixel in line:
                    pixel = pixel.replace('[', '')
                    pixel = pixel.replace(']', '')
                    pixel = pixel.replace(' ', '')
                    pixel_list = []
                    for value in pixel.split(','):
                        pixel_list.append(int(value))
                    line_list.append(pixel_list)
                self.pixels.append(line_list)
        self._cut_into_quarters()
        self._join_up_quarters()

    def _write_pixels_to_file(self, filename):
        with open(filename, 'w') as file:
            for line in self.rearranged_pixels:
                for value in line:
                    file.write(f'{str(value)};')
                file.write('\n')

    def convert_pixels_file(self, filename):
        self._read_pixels_from_file(DATA_FOLDER / f'{filename}.pixels')
        self._write_pixels_to_file(DATA_FOLDER / f'{filename}-r.pixels')


class ImageConverter:
    def __init__(self):
        self.image_path = IMAGE_PATH
        self.data_path = DATA_FOLDER
        self.qty_rows = MATRIX_ROWS
        self.qty_cols = MATRIX_COLS

    def _calculate_sizes(self, pillow_img, qty_art_pixel_col):
        width = pillow_img.size[0]
        height = pillow_img.size[1]
        pixel_resolution = int(width / qty_art_pixel_col)
        center_offset = int(pixel_resolution / 2)

        return width, height, pixel_resolution, center_offset
    
    def convert(self, filename, brightness=10):
        with Image.open(self.image_path / f'{filename}.png') as im:

            #check for multilayer picture (rgb)
            if type(im.getpixel((0, 0))) == int:
                im = im.convert('RGB')
            width, height, pixel_resolution, center_offset = self._calculate_sizes(im, self.qty_cols)

        pixels = []
        for y in range(self.qty_cols):
            row = []
            for x in range(self.qty_rows):
                rgb = []
                for count, value in enumerate(im.getpixel((x*pixel_resolution+center_offset, y*pixel_resolution+center_offset))):
                    if count == 3:
                        break
                    value = int(value * brightness)
                    rgb.append(value)
                row.append(rgb)
            pixels.append(row)

        with open(self.data_path / f'{filename}.pixels', 'w') as file:
            for row in pixels:
                for value in row:
                    file.write(f'{str(value)};')
                file.write('\n')


class AnimationConfig:
    def __init__(self):
        self.data = {}
        self.config_folder = ANI_CONFIGS

    def read(self, filename):
        with open(self.config_folder / f'{filename}.ani', 'r') as file:
            for line in file:
                items = line.split('=')
                self.data[items[0]] = items[1].replace('\n', '')

    def write(self, filename):
        with open(self.config_folder / f'{filename}.ani', 'x') as file:
            for key, value in self.data.items():
                file.write(f'{key}={value}\n')


class Letter:
    def __init__(self, letter):
        self.letter = letter
        self.pixel_columns = []
        self._load_letter()

    def _load_letter(self):
        path = LETTERS_PATH / f'{self.letter}.pixels'
        if self.letter == ' ':
            path = LETTERS_PATH / 'space.pixels'
        elif self.letter == '.':
            path = LETTERS_PATH / 'dot.pixels'
        elif self.letter == '-':
            path = LETTERS_PATH / 'minus.pixels'
        elif self.letter == ':':
            path = LETTERS_PATH / 'colon.pixels'
        elif self.letter == ';':
            path = LETTERS_PATH / 'semicolon.pixels'
        elif self.letter == '?':
            path = LETTERS_PATH / 'questionmark.pixels'
        elif self.letter == ',':
            path = LETTERS_PATH / 'comma.pixels'
        elif self.letter == '=':
            path = LETTERS_PATH / 'equal.pixels'
        elif self.letter == '!':
            path = LETTERS_PATH / 'exclamation.pixels'
        elif self.letter == '+':
            path = LETTERS_PATH / 'plus.pixels'
        
        with open(path) as file:
            for line in file:
                line = line.replace('\n', '')
                self.pixel_columns.append(line)


class Word:
    def __init__(self, word, size):
        self.word = word + "    "
        self.size = size
        self.letters = []
        self._load_letters()
        self.pixel_word = None

    def _load_letters(self):
        for letter in self.word:
            self.letters.append(Letter(letter))

    def _last_col_is_empty(self, letter):
        for col in letter:
            if col.split(';')[-2] != "[0, 0, 0]":
                return False
        return True

    def _append_letter(self, letter):
        for i in range(len(self.pixel_word)):
            # if not self._last_col_is_empty(letter):
            #     self.pixel_word[i] = self.pixel_word[i] + '[0, 0, 0];'
            self.pixel_word[i] = self.pixel_word[i] + letter[i]

    def _merge_all_letters(self):
        self.letters.reverse()
        self.pixel_word = self.letters.pop().pixel_columns
        while self.letters:
            self._append_letter(self.letters.pop().pixel_columns)

    def store_word(self):
        self._merge_all_letters()
        with open(WORDS_PATH / f'{self.word}-{self.size}.pixels', 'w') as file:
            for i in range(len(self.pixel_word)):
                self.pixel_word[i] = self.pixel_word[i].replace('\r', '')
            for row in self.pixel_word:
                file.write(f'{row}\n')


class Surface:
    def __init__(self, width=MATRIX_COLS, height=MATRIX_ROWS):
        self.width = width
        self.height = height
        self.surface = []
        self.pixels = []
        self._create_surface()

    def _create_surface(self):
        for y in range(self.height):
            self.surface.append([])
            for _ in range(self.width):
                self.surface[y].append([0, 0, 0])

    def _read_pixels_file(self, folder, filename):
        self.pixels.clear()
        with open(folder / f'{filename}.pixels', 'r') as file:
            for line in file:
                line = line.rstrip()
                line = line.split(';')
                del line[-1]
                line_list = []
                for pixel in line:
                    pixel = pixel.replace('[', '')
                    pixel = pixel.replace(']', '')
                    pixel = pixel.replace(' ', '')
                    pixel_list = []
                    for value in pixel.split(','):
                        pixel_list.append(int(value))
                    line_list.append(pixel_list)
                self.pixels.append(line_list)

    def add(self, x_offset, y_offset, folder, filename):
        self._read_pixels_file(folder, filename)
        y_length = len(self.pixels)
        x_length = len(self.pixels[0])
        err_counter = 0
        for y in range(y_length):
            for x in range(x_length):
                try:
                    if x + x_offset < 0 or y + y_offset < 0:
                        self.surface[y+y_offset][x+x_offset] = [0, 0, 0]
                    else:
                        self.surface[y+y_offset][x+x_offset] = self.pixels[y][x]
                except IndexError:
                    if err_counter == 0:
                        print(f'WARNING: Not enough place on Surface for file "{filename}"')
                    else:
                        pass
                    err_counter = 1

    def change_brightness(self, br_in_percent):
        for y in range(self.height):
            for x in range(self.width):
                new_pixel_value = []
                for value in self.surface[y][x]:
                    new_pixel_value.append(int(value*br_in_percent*0.01))
                self.surface[y][x] = new_pixel_value

    def write(self, folder, filename):
        with open(folder / f'{filename}.pixels', 'w') as file:
            for line in self.surface:
                for value in line:
                    file.write(f'{str(value)};')
                file.write('\n')


class Weather:
    def __init__(self, icon_folder, key):
        self.icon_folder = icon_folder
        self.key = key
        self.id = None
        self.main = None
        self.desc = None
        self.icon_name = None
        self.city = None
        self.temp = None
        self.humidity = None
        self.icon_filename = None

    def get_weather(self):
        r = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat=51.44328996681601&lon=7.353236392707616&appid={self.key}&units=metric&lang=de')
        current_weather = r.json()
        # current_weather = current_weather['weather'][0]
        self.id = current_weather['weather'][0]['id']
        self.main = current_weather['weather'][0]['main'].upper()
        self.desc = current_weather['weather'][0]['description']
        self.icon_name = current_weather['weather'][0]['icon']
        self.city = current_weather['name'].upper()
        self.temp = int(round(current_weather['main']['temp']))
        self.humidity = int(round(current_weather['main']['humidity']))
        self._choose_icon_filename()

    def _choose_icon_filename(self):
        if self.main == 'Thunderstorm'.upper():
            self.icon_filename = 'lightning'
        elif self.main == 'Drizzle'.upper():
            self.icon_filename = 'rain'
        elif self.main == 'Rain'.upper():
            self.icon_filename = 'rain'
        elif self.main == 'Snow'.upper():
            self.icon_filename = 'snow'
        elif self.main == 'Atmosphere'.upper():
            self.icon_filename = 'cloud'
        elif self.main == 'Clear'.upper():
            self.icon_filename = 'moon'
        elif self.main == 'Clouds'.upper():
            self.icon_filename = 'cloud'
        else:
            raise Exception(f'Unknown Weather Name: {self.main}')
        print('icon filename', self.icon_filename)


class UserInterface:
    def __init__(self):
        self.sender = UARTSender()
        self.converter = PixelsConverter()
        self.ani_conf = AnimationConfig()
        self.weather = Weather(ICONS_PATH, WEATHER_API_KEY)
        self.news = News(NEWS_API_KEY)

    def _show_pixel_data(self):
        filename = input('Please enter a pixels-file-filename from the folder "data": ')
        self.converter.convert_pixels_file(filename)
        self.sender.send_pixels_data(f'{filename}-r.pixels')

    def _show_animation(self):
        filename = input('Filename of the Animation-Configuration-File: ')
        self.sender.send_animation_data(filename)

    def _show_word(self):
        user_input = input('Please enter a Word (only uppercase): ')
        size = 5
        word = Word(user_input, size)
        word.store_word()
        surf = Surface()
        surf.add(0, 0, WORDS_PATH, f'{word.word}-{size}')
        user_input = input('Please enter brightness in %: ')
        surf.change_brightness(int(user_input))
        surf.write(DATA_FOLDER, f'{word.word}.surface')
        self.converter.convert_pixels_file(f'{word.word}.surface')
        self.sender.send_pixels_data(f'{word.word}.surface-r.pixels')

    def _show_scroll_word(self):
        user_input = input('Please enter a Word (only uppercase): ')
        size = 5
        word = Word(user_input, size)
        word_len = len(word.letters)
        print(f'Word letters qty: {word_len - 2}' )
        word.store_word()
        surf = Surface()
        surf.add(0, 0, WORDS_PATH, f'{word.word}-{size}')
        user_input = input('Please enter brightness in %: ')
        surf.change_brightness(int(user_input))
        surf.write(DATA_FOLDER, f'{word.word}.surface')
        self.converter.convert_pixels_file(f'{word.word}.surface')
        self.sender.send_pixels_data(f'{word.word}.surface-r.pixels')
        time.sleep(1)
        for i in range(1, int(word_len/2)):
            surf.add(i *(-10), 0, WORDS_PATH, f'{word.word}-{size}')
            #user_input = input('Please enter brightness in %: ')
            surf.change_brightness(int(user_input))
            surf.write(DATA_FOLDER, f'{word.word}.surface')
            self.converter.convert_pixels_file(f'{word.word}.surface')
            self.sender.send_pixels_data(f'{word.word}.surface-r.pixels', half=True)
            time.sleep(0.3)

    def _show_news(self):
        user_input_source = input('Please enter a news source name(only uppercase): ')
        user_input = input('Please enter a headline text(only uppercase): ')
        size = 5

        headline = Word(user_input, size)
        headline_len = len(headline.letters)
        print(f'Word letters qty: {headline_len - 2}' )
        headline.store_word()

        news_source = Word(user_input_source, size)
        news_source.store_word()

        surf = Surface()
        surf.add(0, 6, WORDS_PATH, f'{headline.word}-{size}')
        surf.add(0, 17, WORDS_PATH, f'{news_source.word}-{size}')
        user_input = input('Please enter brightness in %: ')
        surf.change_brightness(int(user_input))
        surf.write(DATA_FOLDER, f'{headline.word}.surface')
        self.converter.convert_pixels_file(f'{headline.word}.surface')
        self.sender.send_pixels_data(f'{headline.word}.surface-r.pixels')
        time.sleep(1)
        for i in range(1, int(headline_len/2)):
            surf.add(i *(-10), 6, WORDS_PATH, f'{headline.word}-{size}')
            #user_input = input('Please enter brightness in %: ')
            surf.change_brightness(int(user_input))
            surf.write(DATA_FOLDER, f'{headline.word}.surface')
            self.converter.convert_pixels_file(f'{headline.word}.surface')
            self.sender.send_pixels_data(f'{headline.word}.surface-r.pixels', half=True)
            time.sleep(0.3)

    def _show_actual_weather(self):
        self.weather.get_weather()
        size = 5
        city = Word(self.weather.city, size)
        city.store_word()
        main = Word(self.weather.main, size)
        main.store_word()
        temp = Word(str(self.weather.temp), size)
        temp.store_word()
        humidity = Word(str(self.weather.humidity), size)
        humidity.store_word()

        surf = Surface()
        surf.add(0, 1, WORDS_PATH, f'{city.word}-{size}')
        surf.add(1, 8, WORDS_PATH, f'{main.word}-{size}')
        surf.add(1, 15, WORDS_PATH, f'{temp.word}-{size}')
        surf.add(1, 22, WORDS_PATH, f'{humidity.word}-{size}')
        surf.add(15, 15, ICONS_PATH, self.weather.icon_filename)

        surf.change_brightness(3)
        surf.write(DATA_FOLDER, f'weather.surface')
        self.converter.convert_pixels_file(f'weather.surface')
        self.sender.send_pixels_data(f'weather.surface-r.pixels')

    def _show_real_news(self):
        user_input = input('Enter a news id: ')
        user_input_brightness = input('Please enter brightness in %: ')
        self.news.get_headlines(user_input)
        size = 5
        for headline_text in self.news.headlines:
            headline_converted = headline_text['title'].upper()
            print(headline_converted)

            headline = Word(headline_converted.upper(), size)
            headline_len = len(headline.letters)
            print(f'Word letters qty: {headline_len - 2}' )
            headline.store_word()

            news_source = Word(user_input.upper(), 5)
            news_source.store_word()

            surf = Surface()
            surf.add(0, 6, WORDS_PATH, f'{headline.word}-{size}')
            surf.add(0, 17, WORDS_PATH, f'{news_source.word}-{size}')
            
            surf.change_brightness(int(user_input_brightness))
            surf.write(DATA_FOLDER, f'{headline.word}.surface')
            self.converter.convert_pixels_file(f'{headline.word}.surface')
            self.sender.send_pixels_data(f'{headline.word}.surface-r.pixels')
            time.sleep(1)
            for i in range(1, int(headline_len/2)):
                surf.add(i *(-10), 6, WORDS_PATH, f'{headline.word}-{size}')
                #user_input = input('Please enter brightness in %: ')
                surf.change_brightness(int(user_input_brightness))
                surf.write(DATA_FOLDER, f'{headline.word}.surface')
                self.converter.convert_pixels_file(f'{headline.word}.surface')
                self.sender.send_pixels_data(f'{headline.word}.surface-r.pixels', half=True)
                time.sleep(0.3)

    def _show_news_ids(self):
        print()
        self.news.get_sources()
        self.news.filter_language('de')
        for source in self.news.sources:
            print(source['id'])
        print()

    def start(self):
        while True:
            print('1 - Show a Pixel File on the LED-Matrix')
            print('2 - Show a Animation on the LED-Matrix')
            print('3 - Show a Word on the the LED-Matrix')
            print('4 - Show a Weather')
            print('5 - Show scroll Word')
            print('6 - Show pseudo News')
            print('7 - Show news source ids')
            print('8 - Show real news')
            print('q - Exit the program')
            user_input = input('Input: ')
            if user_input == '1':
                self._show_pixel_data()
            elif user_input == '2':
                self._show_animation()
            elif user_input == '3':
                self._show_word()
            elif user_input == '4':
                self._show_actual_weather()
            elif user_input == '5':
                self._show_scroll_word()
            elif user_input == '6':
                self._show_news()
            elif user_input == '7':
                self._show_news_ids()
            elif user_input == '8':
                self._show_real_news()
            elif user_input == 'q':
                break
            else:
                print('Wrong Input. Please try again')


class News:
    def __init__(self, api_key):
        self.api_key = api_key
        self.sources = None
        self.headlines = None

    def get_sources(self):
        self.sources = requests.get(f'https://newsapi.org/v2/top-headlines/sources?apiKey={self.api_key}').json()['sources']

    def filter_language(self, language):
        tmp_list = []
        for source in self.sources:
            if source['language'] == language:
                tmp_list.append(source)
        self.sources.clear()
        self.sources = tmp_list

    def get_headlines(self, source):
        self.headlines = requests.get(f'https://newsapi.org/v2/top-headlines?sources={source}&apiKey={self.api_key}').json()['articles']


class MQTTClient:
    def __init__(self, broker_ip, device_name=DEVICE_NAME, username=USERNAME, password=PASSWORD):
        self.broker_ip = broker_ip
        self.device_name = device_name
        self.username = username
        self.password = password
        self.client = pahoMqtt.Client(self.device_name, clean_session=True)

        self.sender = UARTSender()
        self.converter = PixelsConverter()
        self.ani_conf = AnimationConfig()
        self.weather = Weather(ICONS_PATH, WEATHER_API_KEY)
        self.news = News(NEWS_API_KEY)
        self.img_converter = ImageConverter()

    def on_connect(self, client, userdata, flags, rc):
        print(f'Connected with result code {rc}')
        self.client.subscribe(f'{COMPUTER_NAME}/#', qos=1)
        self.client.subscribe(f'{DEVICE_NAME}/#', qos=1)
        self.client.publish(f'{DEVICE_NAME}/status', 'online', qos=1)

    def on_message(self, client, userdata, msg):
        print(f'{msg.topic} {msg.payload}')

    def on_show_scroll_text(self, client, userdata, msg):
        size = 5
        text = msg.payload.decode()
        word = Word(text, size)
        word_len = len(word.letters)
        print(f'Word letters qty: {word_len - 2}' )
        word.store_word()
        surf = Surface()
        surf.add(0, 0, WORDS_PATH, f'{word.word}-{size}')
        user_input = '10' #input('Please enter brightness in %: ')
        surf.change_brightness(int(user_input))
        surf.write(DATA_FOLDER, f'{word.word}.surface')
        self.converter.convert_pixels_file(f'{word.word}.surface')
        self.sender.send_pixels_data(f'{word.word}.surface-r.pixels')
        time.sleep(1)
        for i in range(1, int(word_len/2)):
            surf.add(i *(-10), 0, WORDS_PATH, f'{word.word}-{size}')
            #user_input = input('Please enter brightness in %: ')
            surf.change_brightness(int(user_input))
            surf.write(DATA_FOLDER, f'{word.word}.surface')
            self.converter.convert_pixels_file(f'{word.word}.surface')
            self.sender.send_pixels_data(f'{word.word}.surface-r.pixels', half=True)
            time.sleep(0.3)

    def on_show_animation(self, client, userdata, msg):
        payload = msg.payload.decode()
        if ',' in payload:
            cmd_list = payload.split(',')
        else:
            cmd_list = [payload]
        print('CMD LIST', cmd_list)
        print('CMD LIST[0]: ', cmd_list[0])
        self.sender.send_animation_data(cmd_list[0])

    def on_show_picture(self, client, userdata, msg):
        img_bytes = msg.payload
        random_filename = token_urlsafe(16)
        image = Image.open(io.BytesIO(img_bytes))
        image.save(CWD / 'pictures' / f'{random_filename}.png')
        self.img_converter.convert(random_filename)
        self.converter.convert_pixels_file(f'{random_filename}')
        self.sender.send_pixels_data(f'{random_filename}-r.pixels')

    def start(self):
        self.client.will_set(f'{DEVICE_NAME}/status', 'offline', qos=1)
        self.client.username_pw_set(self.username, self.password)
        self.client.enable_logger(logger=logger)
        self.client.message_callback_add(f'{DEVICE_NAME}/scroll_text', self.on_show_scroll_text)
        self.client.message_callback_add(f'{DEVICE_NAME}/animation', self.on_show_animation)
        self.client.message_callback_add(f'{DEVICE_NAME}/picture', self.on_show_picture)

        # callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect_async(self.broker_ip, 1884, 10)
        self.client.loop_start()


def main():
    while True:
        print('a - Start UserInterface')
        print('b - Start MQTTClient')
        user_input = input('Input: \n')
        if user_input == 'a':
            user_interface = UserInterface()
            user_interface.start()
            break
        elif user_input == 'b':
            broker_ip = input('Please Enter the Broker IP: ')
            mqtt_client = MQTTClient(broker_ip)
            mqtt_client.start()
            # break
        else:
            print('Wrong Input. Try again.')


if __name__ == '__main__':
    main()
