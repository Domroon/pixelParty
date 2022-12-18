from machine import Pin
from neopixel import NeoPixel
import time
import gc


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
    def __init__(self):
        pass


class PixelParty:
    def __init__(self, pin_num):
        self.pin = Pin(pin_num, Pin.OUT)
        self.matrix = Matrix(self.pin, [])
        self.tick = 0.1

    def _reset_matrix(self):
        self.matrix.clear()
        self.matrix.delete_sprite_groups()

    def show_picture(self, filename):
        self._reset_matrix()
        sprite = Sprite()
        sprite.read_pixels_from_file(filename)
        spriteGroup = SpriteGroup(sprite_list=[sprite])
        self.matrix.sprite_groups = [spriteGroup.sprites_list]
        self.matrix.show()
        
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

    def show_time(self):
        pass

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

        test = 0
        spriteGroup.move(16, 0)
        while test < (len(text)*5+20):
            self.matrix.sprite_groups = [spriteGroup.sprites_list]
            self.matrix.show()
            time.sleep(0.1)
            spriteGroup.move(-1, 0)
            # self.matrix.clear()
            test += 1
            # for sprite_group in self.matrix.sprite_groups:
            #     for sprite in sprite_group:
            #         print(sprite.pixels)

    def show_animation(self):
        pass


def main():
    pixelParty = PixelParty(33)
    try:
        while True:
            pixelParty.show_picture('super_mario_4.pixels')
            time.sleep(1)
            # pixelParty.show_all_signs()
            gc.collect()
            pixelParty.show_text('BAUMHAUS')
    except KeyboardInterrupt:
        pixelParty.matrix.clear()
        pixelParty.matrix.delete_sprite_groups()
       
    
if __name__ == '__main__':
    main()