import time
from pathlib import Path
from PIL import Image

import wiringpi
import RPi.GPIO as GPIO


IRQ_PIN = 4
OUTPUT_MODE = 1
BAUDRATE = 38400

CWD = Path.cwd()
DATA_FOLDER = CWD / 'data'
ANI_CONFIGS = CWD / 'ani_configs'
IMAGE_PATH = CWD / 'pixel_images'
WORDS_PATH = CWD / 'words'
LETTERS_PATH = CWD / 'letters'

MATRIX_COLS = 32
MATRIX_ROWS = 32
PIC_BRIGHTNESS = 10


class UARTSender:
    def __init__(self):
        self.ani_conf = AnimationConfig()
        wiringpi.wiringPiSetupGpio()
        wiringpi.pinMode(IRQ_PIN, OUTPUT_MODE)
        self.serial = wiringpi.serialOpen('/dev/ttyS0', BAUDRATE)

    def _send_data(self, data):
        counter = 0
        for line in data:
            wiringpi.serialPuts(self.serial, line)
            wiringpi.serialPuts(self.serial, '\n')
            print(counter, line)
            counter = counter + 1
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

    def send_pixels_data(self, filename):
        self._trigger_irq()
        time.sleep(0.03)
        wiringpi.serialPuts(self.serial, 'PIXELS')
        wiringpi.serialPuts(self.serial, '\n')
        time.sleep(0.03)
        pixel_strings = self._read_pixels_file(filename)
        self._send_data(pixel_strings)

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
        self._send_data(lines)


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
        with open(LETTERS_PATH / f'{self.letter}.pixels') as file:
            for line in file:
                line = line.replace('\n', '')
                self.pixel_columns.append(line)


class Word:
    def __init__(self, word, size):
        self.word = word
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
            if not self._last_col_is_empty(letter):
                self.pixel_word[i] = self.pixel_word[i] + '[0, 0, 0];'
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
        for y in range(y_length):
            for x in range(x_length):
                self.surface[y+y_offset][x+x_offset] = self.pixels[y][x]

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
        

class UserInterface:
    def __init__(self):
        self.sender = UARTSender()
        self.converter = PixelsConverter()
        self.ani_conf = AnimationConfig()

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

    def start(self):
        while True:
            print('1 - Show a Pixel File on the LED-Matrix')
            print('2 - Show a Animation on the LED-Matrix')
            print('3 - Show a Word on the the LED-Matrix')
            print('q - Exit the program')
            user_input = input('Input: ')
            if user_input == '1':
                self._show_pixel_data()
            elif user_input == '2':
                self._show_animation()
            elif user_input == '3':
                self._show_word()
            elif user_input == 'q':
                break
            else:
                print('Wrong Input. Please try again')


def main():
    user_interface = UserInterface()
    user_interface.start()


if __name__ == '__main__':
    main()
