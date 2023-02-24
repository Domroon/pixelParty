import time
from pathlib import Path
import wiringpi
import RPi.GPIO as GPIO


IRQ_PIN = 4
OUTPUT_MODE = 1
BAUDRATE = 38400

DATA_FOLDER = Path.cwd() / 'data'


class UARTSender:
    def __init__(self):
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


class UserInterface:
    def __init__(self):
        self.sender = UARTSender()
        self.converter = PixelsConverter()

    def _show_pixel_data(self):
        filename = input('Please enter a pixels-file-filename from the folder "data": ')
        self.converter.convert_pixels_file(filename)
        self.sender.send_pixels_data(f'{filename}-r.pixels')

    def show_animation(self):
        pass

    def start(self):
        while True:
            print('1 - Show a Pixel File on the LED-Matrix')
            print('q - Exit the program')
            user_input = input('Input: ')
            if user_input == '1':
                self._show_pixel_data()
            elif user_input == 'q':
                break
            else:
                print('Wrong Input. Please try again')


def main():
    user_interface = UserInterface()
    user_interface.start()


if __name__ == '__main__':
    main()
