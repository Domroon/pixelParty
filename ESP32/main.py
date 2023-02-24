import time
from machine import Pin, UART
from neopixel import NeoPixel
from random import randint
import gc


MATRIX_PIN = 33
UART_TX_PIN = 12
UART_RX_PIN = 14
IRQ_PIN = 35
BAUDRATE = 38400


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

    def write_to_led(self, string_list):
        # self.pixels.clear()
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

    # def write_to_led(self):
    #     for i in range(self.np.n):
    #         self.np[i] = self.pixels[i]
    #     self.np.write()

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


class UARTReceiver:
    def __init__(self):
        self.uart = UART(1, baudrate=BAUDRATE, tx=UART_TX_PIN, rx=UART_RX_PIN, timeout=1000)
        self.command = None
        self.data = []
        
    def receive(self):
        while True:
            line = self.uart.readline()
            if line:
                break
            time.sleep(0.03)
        if line == b'PIXELS\n':
            self.command = 'PIXELS'
            print('Received command "PIXELS"')
            self._receive_pixels_data()
        elif line == b'ANI\n':
            self.command = 'ANI'
            print('Received command "ANI"')
            self._receive_ani_data()
        else:
            raise Exception(f'Unknown Command from UART: {line}')
    
    def _receive_pixels_data(self):
        self.data.clear()
        gc.collect()
        # counter = 0
        start_time = time.ticks_ms()
        while True:
            line = self.uart.readline()
            if line == b'EOF':
                break
            if line:
                self.data.append(line)
                # print(counter, line)
                # counter = counter + 1
        self.data.pop()
        stop_time = time.ticks_ms()
        diff_time = time.ticks_diff(stop_time, start_time)
        print(f'Received Pixels-Data in {diff_time} ms')
    
    def _receive_ani_data(self):
        print('It should now receive the animation type and parameters for that type')


class Device:
    def __init__(self):
        self.pin = Pin(MATRIX_PIN, Pin.OUT)
        self.np = NeoPixel(self.pin, 1024)
        self.matrix = Matrix(self.np)
        self.ani = Animation(self.np)
        self.rec = UARTReceiver()
        self.irq_btn = Pin(IRQ_PIN, Pin.IN)
        self.mode = None
        self.data = None
        self.run_loops = False

    def _listen_uart(self, pin):
        self.data = None
        print('receive data...')
        self.rec.receive()
        print('sucessfully received data')
        self.mode = self.rec.command
        self.data = self.rec.data
        self.run_loops = False
        # for value in self.rec.data:
        #    print(value)
        print('length:', len(self.rec.data))
        self._show_on_matrix()
        # print('mode', self.mode)
        # print('data', self.data)
        # print('length', len(self.data))

    def _show_on_matrix(self):
        self.matrix.clear()
        if self.mode == 'PIXELS':
            self.matrix.write_to_led(self.data)
        elif self.mode == 'ANI':
            self.run_loops = True
            while True:
                if not self.run_loops:
                    break
                print('Show Animation')
                time.sleep(1)

    def start(self):
        self.irq_btn.irq(self._listen_uart, trigger=self.irq_btn.IRQ_RISING)

        
def main():
    device = Device()
    device.start()


if __name__ == '__main__':
    main()