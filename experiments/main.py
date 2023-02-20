import time
from machine import Pin
from neopixel import NeoPixel
import gc


class Picture:
    def __init__(self, np):
        self.np = np
        self.pixels = []

    def _rearrange(self):
        for index, line in enumerate(self.pixels):
            if index % 2 == 0:
                line.reverse()

    def read_pixels_from_file(self, path):
        self.pixels.clear()
        with open(path, 'r') as file:
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
        self._rearrange()


    def write_to_led(self):
        for line_no, line in enumerate(self.pixels):
            for pixel_no, pixel in enumerate(line):
                    self.np[pixel_no + line_no * 16] = pixel
        self.np.write()

def main():
    pin = Pin(33, Pin.OUT)
    np = NeoPixel(pin, 256)
    pic = Picture(np)

    pic.read_pixels_from_file('lightning.pixels')
    pic.write_to_led()
    time.sleep(1)
    
    pic.read_pixels_from_file('super_mario-5.pixels')
    pic.write_to_led()
    time.sleep(1)
    
    pic.read_pixels_from_file('cloud.pixels')
    pic.write_to_led()
    time.sleep(1)
    
    pic.read_pixels_from_file('chess_red-5.pixels')
    pic.write_to_led()
    time.sleep(1)
    
    pic.read_pixels_from_file('chess_purple-5.pixels')
    pic.write_to_led()
    time.sleep(1)
    
    pic.read_pixels_from_file('cross_blue-5.pixels')
    pic.write_to_led()
    time.sleep(1)
    
    pic.read_pixels_from_file('cross_green-5.pixels')
    pic.write_to_led()
    time.sleep(1)
    
    pic.read_pixels_from_file('rain.pixels')
    pic.write_to_led()
    time.sleep(1)

    np.fill((0,0,0))
    np.write()
    print(f'Allocated Memory: {gc.mem_alloc()}')
    print(f'Free Memory: {gc.mem_free()}')


if __name__ == '__main__':
    main()