import time
from machine import Pin
from neopixel import NeoPixel
import gc


class Matrix:
    def __init__(self, np):
        self.np = np
        self.pixels = []

    def _rearrange(self):
        upper_half = []
        bottom_half = []
        half = int(len(self.pixels) / 2)
        for i in range(0, half):
            upper_half.append(self.pixels[i])

        for i in range(half, int(len(self.pixels))):
            bottom_half.append(self.pixels[i])

        
        # for index, line in enumerate(self.pixels):
        #     if index % 2 == 0:
        #         line.reverse()
        print('UPPER')
        self._cut_in_half(upper_half)
        print('BOTTOM')
        self._cut_in_half(bottom_half)
        
    def _cut_in_half(self, half):
        left_quarter = []
        right_quarter = []
        half_index = int(len(half[0]) / 2)
        for line in half:
            for i in range(half_index):
                left_quarter.append(line[i])
            for i in range(half_index, int(len(half[0]))):
                right_quarter.append(line[i])
        print('LEFT_QUARTER')
        for line in left_quarter:
            print(line)
        print('RIGHT_QUARTER')
        for line in right_quarter:
            print(line)


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
    np = NeoPixel(pin, 1024)
    matrix = Matrix(np)
    
    matrix.read_pixels_from_file('face.pixels')
    matrix.write_to_led()
    time.sleep(10)

    np.fill((20,20,20))
    np.write()
    time.sleep(1)
    np.fill((0,0,0))
    np.write()

    matrix.read_pixels_from_file('lightning.pixels')
    matrix.write_to_led()
    time.sleep(1)
    
    
    # matrix.read_pixels_from_file('super_mario-5.pixels')
    # matrix.write_to_led()
    # time.sleep(1)
    
    # matrix.read_pixels_from_file('cloud.pixels')
    # matrix.write_to_led()
    # time.sleep(1)
    
    # matrix.read_pixels_from_file('chess_red-5.pixels')
    # matrix.write_to_led()
    # time.sleep(1)
    
    # matrix.read_pixels_from_file('chess_purple-5.pixels')
    # matrix.write_to_led()
    # time.sleep(1)
    
    # matrix.read_pixels_from_file('cross_blue-5.pixels')
    # matrix.write_to_led()
    # time.sleep(1)
    
    # matrix.read_pixels_from_file('cross_green-5.pixels')
    # matrix.write_to_led()
    # time.sleep(1)
    
    # matrix.read_pixels_from_file('rain.pixels')
    # matrix.write_to_led()
    # time.sleep(1)

    np.fill((0,0,0))
    np.write()
    print(f'Allocated Memory: {gc.mem_alloc()}')
    print(f'Free Memory: {gc.mem_free()}')


if __name__ == '__main__':
    main()