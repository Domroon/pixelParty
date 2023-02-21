import time
from machine import Pin
from neopixel import NeoPixel
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

    def write_to_led(self):
        for i in range(self.np.n):
            self.np[i] = self.pixels[i]
        self.np.write()


def main():
    pin = Pin(33, Pin.OUT)
    np = NeoPixel(pin, 1024)
    matrix = Matrix(np)

    matrix.read_pixels_from_file('edge-points-r.pixels')
    matrix.write_to_led()
    # time.sleep(1)
    
    matrix.read_pixels_from_file('face-r.pixels')
    matrix.write_to_led()
    time.sleep(10)

    np.fill((0,0,0))
    np.write()
    print(f'Allocated Memory: {gc.mem_alloc()}')
    print(f'Free Memory: {gc.mem_free()}')


if __name__ == '__main__':
    main()