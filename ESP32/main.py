import time
from machine import Pin, UART
from random import randint
import gc


class Matrix:
    def __init__(self, np):
        self.np = np
        self.pixels = []

    def read_pixels_from_file(self, path):
        self.pixels.clear()
        with open(path, 'r') as file:
            for line in file:
                gc.collect()
                line = line.rstrip()
                line = line.split(';')
                del line[-1]
                # line_list = []
                for pixel in line:
                    pixel = pixel.replace('[', '')
                    pixel = pixel.replace(']', '')
                    pixel = pixel.replace(' ', '')
                    pixel_list = []
                    for value in pixel.split(','):
                        pixel_list.append(int(value))
                    self.pixels.append(pixel_list)

    def read_pixels_from_string_list(self, string_list):
        pixels_string = []
        for line in string_list:
            pixels_string.append(line.decode().rstrip())  

        print(pixels_string) 

    def write_to_led(self):
        for i in range(self.np.n):
            self.np[i] = self.pixels[i]
        self.np.write()


class Animation:
    def __init__(self, np, brightness=10):
        self.np = np
        self.br = brightness

    def _clear(self):
        self.np.fill((0, 0, 0))
        self.np.write()
    
    def random_color_flash(self):
        self.np[randint(0, self.np.n - 1)] = (255, 255, 255)
        self.np[randint(0, self.np.n - 1)] = (255, 0, 0)
        self.np[randint(0, self.np.n - 1)] = (0, 255, 0)
        self.np[randint(0, self.np.n - 1)] = (0, 0, 255)
        self.np[randint(0, self.np.n - 1)] = (255, 0, 255)
        self.np[randint(0, self.np.n - 1)] = (0, 255, 255)
        self.np.write()
        self._clear()

    def random_colors(self):
        for pos in range(0, self.np.n - 1):
            max = randint(0, self.br)
            self.np[pos] = (randint(0, max), randint(0, max), randint(0, max))
        self.np.write()


class Receiver:
    def __init__(self):
        self.uart = UART(1, baudrate=115200, tx=12, rx=14)
        self.lines = []
        
    def receive(self):
        while True:
            line = self.uart.readline()
            if line:
                break
            time.sleep(0.03)
        line = line.decode()
        if line == 'PIXELS':
            self._receive_pixels_data()
        elif line == 'ANI':
            self._receive_ani_data()
        else:
            raise Exception('Unknown Command from UART')
    
    def _receive_pixels_data(self):
        self.lines.clear()
        while True:
            line = self.uart.readline()
            if line:
                # print(line)
                self.lines.append(line)
            if line == b'EOF':
                break
        self.lines.pop()
    
    def _receive_ani_data(self):
        print('It should now receive the animation type and parameters for that type')