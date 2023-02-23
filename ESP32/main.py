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