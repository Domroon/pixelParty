import network
import socket
import time
import urequests as requests


LINK = {
    'ip-info': 'http://ip-api.com/json/',
    'datetime': 'https://timeapi.io/api/Time/current/zone?timeZone=Europe/Berlin'
}

CONTENT = b"""\
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ESP 32 Test</title>
  </head>
  <body>
    <h1>This is a test :)</h1>
  </body>
</html>
"""


class ConnectionError(Exception):
    """Raises when there is no connection after connect call"""

class InternetError(Exception):
    """Raises when the Router have no connection to the Internet"""


class Client:
    def __init__(self, logger):
        self.wlan = network.WLAN(network.STA_IF)
        self.log = logger
        self.available_networks = []
        self.stored_networks = []
        self._read_stored_networks()

    def _read_stored_networks(self):
        with open("stored_networks.txt", 'r') as file:
            lines = file.read().splitlines()
            for line in lines:
                value = line.split('|')
                if value[1] == 'None':
                    value[1] = None
                self.stored_networks.append({'ssid': value[0], 'key': value[1]})
            
            for network in self.stored_networks:
                self.log.debug(network['ssid'])

    def activate(self):
        self.wlan.active(True)

    def search_wlan(self):
        self.log.info("Searching available networks")
        for wlan in self.wlan.scan():
            wlan_name = wlan[0].decode()
            debug_str = "Available Network: " + wlan_name
            self.log.debug(debug_str)
            self.available_networks.append(wlan_name)

    def connect(self):
        for network in self.stored_networks:
            if network['ssid'] in self.available_networks:
                if not self.wlan.isconnected():
                    log_str = "Connecting to " + network['ssid'] + "..."
                    self.log.info(log_str)
                    self.wlan.connect(network['ssid'], network['key'])
                    time.sleep(5)
                else:
                    log_str = "Already connected to: " + network['ssid']
                    self.log.info(log_str)
                
                if self.wlan.isconnected():
                    log_str = "Connected to " + network['ssid']
                    self.log.info(log_str)
                else:
                    raise ConnectionError("No connection after connect call")
        
        if not self.wlan.isconnected():
            raise ConnectionError("Saved networks are not available")
    
    def disconnect(self):
        self.log.info('Disconnect')
        self.wlan.disconnect()

    def deactivate(self):
        self.log.info('Wlan client deactivated')
        self.wlan.active(False)
        

class Server:
    def __init__(self, logger, micropython_optimize=False):
        self.ap = network.WLAN(network.AP_IF)
        self.log = logger
        self.optimize = micropython_optimize
        self.ssid = 'ESP-Matrix-AP'
        self.ip = None
        self.subnet = None
        self.gateway = None
        self.dns = None

    def _configure_server(self):
        self.ap.config(essid=self.ssid)
        self.ap.config(max_clients=1)
        time.sleep(2)

        config_data = self.ap.ifconfig()
        self.ip = config_data[0]
        self.subnet = config_data[1]
        self.gateway = config_data[2]
        self.dns = config_data[3]
        self.log.info('Server configured')
        self.log.debug('IP: ' + self.ip)
        self.log.debug('Subnet: ' + self.subnet)
        self.log.debug('Gateway: ' + self.gateway)
        self.log.debug('DNS: ' + self.dns)
        self.log.info('SSID: ' + self.ssid)

    def activate(self):
        self.ap.active(True)
        self._configure_server()
    
    def wait_for_connection(self):
        if not self.ap.isconnected():
            self.log.info('Waiting for connection...')
            while not self.ap.isconnected():
                time.sleep(1)

            time.sleep(1)
            self.log.info('Connected')
        else:
            time.sleep(1)
            self.log.info('Connected')

    def deactivate(self):
        self.ip = None
        self.subnet = None
        self.gateway = None
        self.dns = None
        self.ap.active(False)
        self.log.info('Access Point Server deactivated')
        
    def _extract_variables(self, http_line):
        line = http_line.decode()
        splitted_line = line.split('?')
        try:
            splitted_line[1] = splitted_line[1].replace('\r\n', '')
            variables_with_values = splitted_line[1].split('&')
            data_dict = {}
            for value_variable in variables_with_values:
                variable = value_variable.split('=')
                data_dict[variable[0]] = variable[1]
            print(data_dict)
        except IndexError:
            print('No data in text-fields')

    def receive_http_data(self):
        s = socket.socket()
        address_info = socket.getaddrinfo('0.0.0.0', 80)
        # self.log.debug('Bind address info: ' + address_info)
        address = address_info[0][-1]
        # self.log.debug('Address: ' + address)

        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(address)
        s.listen(5)
        info_str = 'Listening, connect your browser to http://' + self.ip + '/'
        self.log.info(info_str)

        run = True
        while run:
            response = s.accept()
            # self.wdt.feed()
            client_socket = response[0]
            client_address = response[1]

            if not self.optimize:
                client_stream = client_socket.makefile('rwb')
            else:
                client_stream = client_socket

            request = client_stream.readline()
            request_type = request.decode().split(" ")[0]
            # self.log.info(request_type + ' request from ' + client_address)
            self.log.debug('Request Details:')
            while True:
                h = client_stream.readline()
                if h == b"" or h == b"\r\n":
                    break
                self.log.debug(h)
                if 'Referer' in h:
                    self._extract_variables(h)
                    run = False
                    break
            
            with open('html_data/index.html', 'r') as file:
                data = file.read().encode()
                client_stream.write(data)

            client_stream.close()
            if not self.optimize:
                client_socket.close()
            print()


def download_json_file(address):
    try:
        r = requests.get(address)
        infos = r.json()
        r.close()
        return infos
    except OSError:
        raise InternetError("No response from the requested server")


def print_ip_infos():
    ip_infos = download_json_file(LINK['ip-info'])
    for key, data in ip_infos.items():
        print(key, ":", data)


