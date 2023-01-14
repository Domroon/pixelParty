from machine import Pin, SoftSPI
from neopixel import NeoPixel
import time
import gc
from machine import RTC
from random import randint

from networking import download_json_file
from networking import LINK
from networking import Client
from ulogging import Logger


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
    def __init__(self, x=0, y=0):
        self.id = id(self)
        self.x = x
        self.y = y
        self.pixels = [
                        Pixel(self.id, 0, 0),
                      ]

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
                    self.pixels.append(pixel)
                x += 1
            y += 1
        gc.collect()
        
    
    def read_pixels_from_file(self, filename):
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
                new_row.append(rgb_list)
            color_array.append(new_row)
        file.close()
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
    def __init__(self, neopixel, sprite_groups, width=16, height=16):
        self.sprite_groups = sprite_groups
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

    def show(self):
        for sprite_group in self.sprite_groups:
            for sprite in sprite_group:
                self._add_sprite(sprite)
        self.np.write()

    def delete_sprite_groups(self):
        self.sprite_groups = []
        
    def clear(self):
        self.np.fill((0, 0, 0))
        self.np.write()
        
    def fill_black(self):
        self.np.fill((0, 0, 0))


class Animation:
    def __init__(self, pin_num, width=16, height=16):
        self.width = width
        self.height = height
        self.pin = Pin(pin_num, Pin.OUT)
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
    def __init__(self, matrix, pin_num):
        self.pin = Pin(pin_num, Pin.OUT)
        self.matrix = matrix
        self.tick = 0.1
        self.rtc = RTC()
        self.animation = Animation(pin_num)

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


def main():
    WIDTH = 16
    HEIGHT = 16
    LED_QTY = WIDTH * HEIGHT
    pin = Pin(33, Pin.OUT)
    neopixel = NeoPixel(pin, LED_QTY)
    logger = Logger()
    matrix = Matrix(neopixel, [])
    pixelParty = PixelParty(matrix, 33)
    # clock = Clock(logger)
    # clock.set_time()
    # print(clock.rtc.datetime())

    # init spi bus
    MOSI = Pin(25)
    MISO = Pin(26)
    SCK = Pin(27)
    chip_select = Pin(32, mode=Pin.IN)

    spi = SoftSPI(mosi=MOSI, miso=MISO, sck=SCK)
    spi.init()

    while True:
        # SPI Communication
        print('Waiting for Data via SPI')
        while True:
            # print(chip_select.value())
            # if chip_select.value() == 0:
            print('Start communication via SPI')
            buffer = spi.read(5)
            break
            time.sleep(0.1)
        print(buffer)
        time.sleep(0.5)

    

    try:
        while True:
            pixelParty.show_all_signs()
            pixelParty.show_text('DORTMUND')
            pixelParty.show_all_animations()
            # pixelParty.show_picture('super_mario_4.pixels')
            time.sleep(1)
    except KeyboardInterrupt:
        pixelParty.matrix.clear()
        pixelParty.matrix.delete_sprite_groups()
       
    
if __name__ == '__main__':
    main()