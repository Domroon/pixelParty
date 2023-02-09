from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler


CWD = Path.cwd()
PAGES_DATA_FOLDER = CWD / 'pages_data'


def config_logger():
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(name)-15s %(message)s')
    formatter_2 = logging.Formatter('%(asctime)s %(levelname)-8s %(name)-15s %(message)s\n')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler('error.log', maxBytes=4096, backupCount=3)
    file_handler.setFormatter(formatter_2)
    file_handler.setLevel(logging.ERROR)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = config_logger()


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

    def _set_log_level(self):
        log_level_name = self.config.data['general']['log_level']
        if log_level_name == 'NOTSET':
            log_level = logging.NOTSET
        elif log_level_name == 'DEBUG':
            log_level = logging.DEBUG
        elif log_level_name == 'INFO':
            log_level = logging.INFO
        elif log_level_name == 'WARNING':
            log_level = logging.WARNING
        elif log_level_name == 'ERROR':
            log_level = logging.ERROR
        elif log_level_name == 'CRITICAL':
            log_level = logging.CRITICAL
        else:
            raise Exception(f'Wrong log level name in config file: "{log_level_name}"')
        logger.setLevel(log_level)

    def start(self):
        self.config.read('master_data.conf')
        self.data.read(PAGES_DATA_FOLDER / self.config.data['general']['pages_filename'])
        self._set_log_level()


def main():
    try:
        pixelParty = PixelParty()
        pixelParty.start()

    except Exception:
        logger.exception("Exception occurred")


if __name__ == '__main__':
    main()