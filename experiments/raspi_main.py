class Matrix:
    def __init__(self):
        self.pixels = []
        self.quarters = {}

    def _cut_into_quarters(self):
        upper_half = []
        bottom_half = []
        half = int(len(self.pixels) / 2)
        for i in range(0, half):
            upper_half.append(self.pixels[i])

        for i in range(half, int(len(self.pixels))):
            bottom_half.append(self.pixels[i])

        upper_left, upper_right = self._cut_in_half(upper_half)
        bottom_left, bottom_right = self._cut_in_half(bottom_half)
        self.quarters = {
            'upper_left': upper_left,
            'upper_right': upper_right,
            'bottom_left': bottom_left,
            'bottom_right': bottom_right
        }
        
        # reverse every second line
        for pixel_list in self.quarters:
            for i, line in enumerate(pixel_list):
                if i % 2 == 0:
                    line.reverse()
           
    def _cut_in_half(self, half):
        left_quarter = []
        right_quarter = []
        half_index = int(len(half[0]) / 2)
        for line in half:
            left_quarter.append([line[i] for i in range(half_index)])
            right_quarter.append([line[i] for i in range(half_index, int(len(half[0])))])

        return left_quarter, right_quarter
        
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
        self._cut_into_quarters()

    def join_up_quarters(self):
        # join up every row from upper_left with every row from upper_right
        # join up every row from bottom_left with every row from bottom_right
        # append the bottom half to the upper half
        pass 


def main():
    matrix = Matrix()
    matrix.read_pixels_from_file('face.pixels')


if __name__ == '__main__':
    main()