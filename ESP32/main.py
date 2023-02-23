import time
from machine import Pin, UART
from neopixel import NeoPixel
from random import randint
import gc


MATRIX_PIN = 33
UART_TX_PIN = 12
UART_RX_PIN = 14
IRQ_PIN = 35


class Matrix:
    def __init__(self):
        self.pin = Pin(MATRIX_PIN, Pin.OUT)
        self.np = NeoPixel(self.pin, 1024)
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

    def read_pixels(self, string_list):
        pixels_string = []
        for line in string_list:
            pixels_string.append(line.decode().rstrip())  

        print(pixels_string) 

    def write_to_led(self):
        for i in range(self.np.n):
            self.np[i] = self.pixels[i]
        self.np.write()

    def clear(self):
        self.np.fill((0, 0, 0))
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
        self.uart = UART(1, baudrate=115200, tx=UART_TX_PIN, rx=UART_RX_PIN)
        self.command = None
        self.data = []
        
    def receive(self):
        while True:
            line = self.uart.readline()
            if line:
                break
            time.sleep(0.03)
        line = line.decode()
        if line == 'PIXELS':
            self.command = 'PIXELS'
            self._receive_pixels_data()
        elif line == 'ANI':
            self.command = 'ANI'
            self._receive_ani_data()
        else:
            raise Exception('Unknown Command from UART')
    
    def _receive_pixels_data(self):
        self.data.clear()
        while True:
            line = self.uart.readline()
            if line:
                # print(line)
                self.data.append(line)
            if line == b'EOF':
                break
        self.data.pop()
    
    def _receive_ani_data(self):
        print('It should now receive the animation type and parameters for that type')


class Device:
    def __init__(self):
        self.matrix = Matrix()
        self.ani = Animation()
        self.rec = Receiver()
        self.irq_btn = Pin(IRQ_PIN, Pin.IN)
        self.mode = None
        self.run_loops = False

    def _listen_uart(self):
        self.rec.receive()
        self.mode = self.rec.command
        self.data = self.rec.data
        self.run_loops = False
        self._show_on_matrix()

    def _show_on_matrix(self):
        self.matrix.clear()
        if self.mode == 'PIXELS':
            self.matrix.read_pixels(self.data)
            self.matrix.write_to_led()
        elif self.mode == 'ANI':
            self.run_loops = True
            while True:
                if not self.run_loops:
                    break
                print('Show Animation')
                time.sleep(1)

    def start(self):
        self.irq_btn.irq(self._listen_uart)


def main():
    device = Device()
    device.start()


if __name__ == '__main__':
    main()