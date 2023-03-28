from pathlib import Path
import threading
from typing import Union
from secrets import token_urlsafe
import io

from fastapi import FastAPI, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import paho.mqtt.client as pahoMqtt
from PIL import Image


USERNAME = "domroon"
PASSWORD = "MPCkY5DGuU19sGgpvQvgYqN8Uw0"
CWD = Path.cwd()
DEVICE_NAME = 'computer-client'
MATRIX_NAME = 'pixel-master'

# logger = getLogger('mqttInput')
# logger.setLevel(mqtt.MQTT_LOG_INFO)

datas = {
    'pixel-master': {'status': 'offline'}
}

class MQTTClient:
    def __init__(self, broker_ip='localhost', device_name=DEVICE_NAME, username=USERNAME, password=PASSWORD):
        self.broker_ip = broker_ip
        self.client = pahoMqtt.Client(DEVICE_NAME, clean_session=False)
        self.device_name = device_name
        self.username = username
        self.password = password

    def on_connect(self, client, userdata, flags, rc):
        print(f'MQTT Client connected with result code {rc} as "{DEVICE_NAME}"')
        client.subscribe(f'{MATRIX_NAME}/#', qos=1)
        client.publish(f'{DEVICE_NAME}/status', 'online', qos=1)

    def on_message(self, client, userdata, msg):
        print(f'{msg.topic} {msg.payload}')

    def on_status(self, client, userdata, msg):
        status = msg.payload.decode('utf-8')
        if status == 'offline':
            datas['pixel-master']['status'] = 'offline'
            print(f'{MATRIX_NAME} is offline')
        if status == 'online':
            datas['pixel-master']['status'] = 'online'
            print(f'{MATRIX_NAME} is online')

    def show_scroll_text(self, text):
        self.client.publish(f'{MATRIX_NAME}/scroll_text', text)

    def show_animation(self, ani_type):
        if ani_type == 'random_colors':
            self.client.publish(f'{MATRIX_NAME}/animation', 'random_colors')
        elif ani_type == 'random_color_flash':
            sleep_time = 1
            self.client.publish(f'{MATRIX_NAME}/animation', f'random_color_flash,{sleep_time}')

    def show_picture(self, byte_data):
        self.client.publish(f'{MATRIX_NAME}/picture', byte_data)

    def show_weather(self, city_name):
        self.client.publish(f'{MATRIX_NAME}/weather', city_name)

    def show_news(self, source_id):
        self.client.publish(f'{MATRIX_NAME}/news', source_id)

    def start(self):
        self.client.will_set(f'{DEVICE_NAME}/status', 'offline', qos=1)
        self.client.username_pw_set(self.username, self.password)

        # callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.message_callback_add(f'{MATRIX_NAME}/status', self.on_status)

        self.client.connect_async(self.broker_ip, 1884, 10)
        self.client.loop_start()


class Text(BaseModel):
    text: str


app = FastAPI()
mqtt_client = MQTTClient()
mqtt_client.start()


origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/pixel-master/status")
async def status():
    return datas['pixel-master']['status']


@app.post("/pixel-master/scroll-text")
async def scroll_text(text: Text):
    mqtt_client.show_scroll_text(text.text)
    return text


@app.post("/pixel-master/animation")
async def animation(ani_type: str = Query("random_color_flash", enum=["random_color_flash", "random_colors"])):
    mqtt_client.show_animation(ani_type)
    return {"ani_type": ani_type}


@app.post("/pixel-master/picture")
async def picture(file: bytes = File("Null")):
    mqtt_client.show_picture(file)
    return {"file_size": len(file), "file": dir(file), "type": str(type(file))}


@app.post("/pixel-master/weather")
async def weather(city_name: Text):
    mqtt_client.show_weather(city_name.text)
    return {"city_name": city_name.text}


@app.post("/pixel-master/news")
async def news(source_id: str = 
    Query("t3n", enum=[
    "t3n",
    "bild",
    "der-tagesspiegel",
    "die-zeit",
    "focus",
    "gruenderszene",
    "handelsblatt",
    "spiegel-online",
    "wired-de",
    "wirtschafts-woche"])):
    mqtt_client.show_news(source_id)
    print("source_id", source_id)
    return {"source_id": source_id}