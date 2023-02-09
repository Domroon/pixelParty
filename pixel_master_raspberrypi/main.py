from pathlib import Path

CWD = Path.cwd()
PAGES_DATA_FOLDER = CWD / 'pages_data'


class ConfigParser:
    def __init__(self):
        self.data = {}

    def read(self, file_path):
        current_section = None
        with open(file_path, 'r') as file:
            for line in file:
                if '[' in line:
                    line = line.replace('[', '').replace(']', '')
                    current_section = line.replace('\r\n', '')
                    current_section = line.replace('\n', '')
                    self.data[current_section] = {}
                else:
                    if line in ['\n', '\r\n']:
                        pass
                    else:
                        key_and_value = line.split('=')
                        key = key_and_value[0]
                        value = key_and_value[1].replace('\r\n', '')
                        value = key_and_value[1].replace('\n', '')
                        self.data[current_section][key] = value

    def write(self, file_path):
        with open(file_path, 'w') as file:
            for key, value in self.data.items():
                file.write(f'[{key}]\r\n')
                for key_2, value_2 in value.items():
                    file.write(f'{key_2}={value_2}\r\n')
                file.write('\n')

    def search_section_for_key(self, searched_key):
        for section_name, section_data in self.data.items():
            for key in section_data.keys():
                if searched_key == key:
                    return section_name
        return None


class DataParser:
    def __init__(self):
        self.data = []

    def _parse_ani_data(self, params):
        params_dict = {
                'page_type': params[0],
                'duration_in_ms': int(params[1]),
                'frame_time_in_ms': int(params[2])
            }
        if params[3] == 'line_top_bottom':
            self._parse_ani_line_top_bottom(params, params_dict)
        elif params[3] == 'full_color':
            self._parse_ani_full_color(params, params_dict)
        elif params[3] == 'color_change':
            self._parse_ani_color_change(params, params_dict)
        elif params[3] == 'random_color_flash':
            self._parse_ani_random_color_flash(params, params_dict)
        else:
            raise Exception(f'Unknown Animation Type: {params[3]}')

    def _parse_ani_line_top_bottom(self, params, params_dict):
        params_dict['ani_name'] = params[3]
        color = params[4].replace('(', '').replace(')', '').split(',')
        params_dict['color'] = (int(color[0]), int(color[1]), int(color[2]))
        self.data.append(params_dict)

    def _parse_ani_full_color(self, params, params_dict):
        params_dict['ani_name'] = params[3]
        color = params[4].replace('(', '').replace(')', '').split(',')
        params_dict['color'] = (int(color[0]), int(color[1]), int(color[2]))
        self.data.append(params_dict)

    def _parse_ani_color_change(self, params, params_dict):
        params_dict['ani_name'] = params[3]
        self.data.append(params_dict)

    def _parse_ani_random_color_flash(self, params, params_dict):
        params_dict['ani_name'] = params[3]
        self.data.append(params_dict)

    def _parse_static_data(self, params):
        params_dict = {}
        params.reverse()
        params_dict['page_type'] = params.pop()
        params_dict['duration_in_ms'] = params.pop()
        params_dict['pixels_data'] = []
        params.reverse()
        for pixel_data in params:
            pixel_data = pixel_data.split(',')
            x_y = pixel_data[3].split('|')
            x = x_y[0]
            y = x_y[1]
            params_dict['pixels_data'].append({
                'pixel_type': pixel_data[0],
                'size': pixel_data[1],
                'file_name': pixel_data[2],
                'coordinates': {'x': x, 'y': y}
            })
        self.data.append(params_dict)

    def read(self, file_path):
        with open(file_path, 'r') as file:
            for line in file:
                params = line.split(';')
                for index, param in enumerate(params):
                    params[index] = param.replace('\r\n', '')
                    params[index] = param.replace('\n', '')
                if params[0] == 'ani':
                    self._parse_ani_data(params)
                elif params[0] == 'static':
                    self._parse_static_data(params)
                else:
                    raise Exception(f'Unknown Page Type: {params[0]}')
                    
    def write(self):
        pass


class PixelParty:
    def __init__(self):
        self.config = ConfigParser()
        self.data = DataParser()

    def start(self):
        self.config.read('master_data.conf')
        self.data.read(PAGES_DATA_FOLDER / self.config.data['general']['pages_filename'])
        for data in self.data.data:
            print(data)


def main():
    pixelParty = PixelParty()
    pixelParty.start()


if __name__ == '__main__':
    main()