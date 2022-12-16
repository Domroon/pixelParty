from machine import Pin
from neopixel import NeoPixel
import time


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
        self.sprites = sprite_list
        
    def add(self, sprite):
        self.sprites.append(sprite)
        
    def remove(self):
        self.sprites.pop()


class Matrix:
    def __init__(self, pin, sprite_groups, width=16, height=16):
        self.pin = pin
        self.sprite_groups = sprite_groups
        self.width = width
        self.height = height
        self.led_qty = width * height
        self.np = NeoPixel(self.pin, self.led_qty)
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
            try:
                self.np[self.coord[pixel.y][pixel.x]] = pixel.color
            except IndexError:
                pass
    
    def show(self):
        for sprite_group in self.sprite_groups:
            for sprite in sprite_group:
                self._add_sprite(sprite)
        self.np.write()
        
    def clear(self):
        self.np.fill((0, 0, 0))
        self.np.write()
        
    def fill_black(self):
        self.np.fill((0, 0, 0))


class Word:
    def __init__(self, sign_size):
        self.spriteGroup = SpriteGroup()
        self.spriteGroup.sprites = []
        self.sign_size = sign_size
        self.x = 0
        self.y = 0
    
    def add_word(self, word_string):
        for count, sign in enumerate(word_string):
            sprite = Sprite()
            sprite.read_pixels_from_file('pixels_data/' + sign + '.pixels')
            sprite.set_pos(count*self.sign_size, 0)
            self.spriteGroup.add(sprite)

    def get_sprites(self):
        return self.spriteGroup.sprites

    def move(self, x, y):
        self.x = x
        self.y = y
        for sprite in self.get_sprites():
            sprite.move(self.x, self.y)
            
    def set_pos(self, x, y):
        for count, sprite in enumerate(self.get_sprites()):
            sprite.set_pos(count*self.sign_size, 0)


def main():
    
    pin = Pin(33, Pin.OUT)

    sprite = Sprite()
    sprite.read_pixels_from_file('super_mario_4.pixels')
    print(sprite.pixels)


    # sprite.read_pixels_from_file('pixels_data/0.pixels')
    # sprite.change_all_color((100, 0, 0))

    # sprite_2 = Sprite()
    # sprite_2.set_pos(5, 5)
    
    # sprite_group_2 = SpriteGroup()
    # sprite_group_2.add(sprite_2)

    spriteGroup = SpriteGroup()
    spriteGroup.add(sprite)

    # first_word = Word(6)
    # first_word.add_word('DORTMUND')
    
    # matrix = Matrix(pin, [sprite_group_2.sprites, spriteGroup.sprites])
    matrix = Matrix(pin, [spriteGroup.sprites])
    tick = 0.1
    try:
#         signs = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
#         while True:
#             for sign in signs:
#                 sprite.read_pixels_from_file('pixels_data/' + sign + '.pixels')
#                 sprite.change_all_color((100, 0, 0))
#                 matrix.show()
#                 time.sleep(0.2)
#                 time.sleep(tick)
        # while True:
        #     matrix.show()
        #     time.sleep(1)
        #     for _ in range(30):
        #         matrix.show()
        #         first_word.move(-1, 0)
        #         time.sleep(tick)
        #         matrix.fill_black()
        #     matrix.show()
        #     first_word.set_pos(0, 0)
        #     time.sleep(tick)
        #     time.sleep(1)
        #     matrix.fill_black()
        matrix.show()
    except KeyboardInterrupt:
        matrix.clear()
       
    
if __name__ == '__main__':
    main()