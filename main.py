import configparser
import datetime
import json
import os
import time
from io import BytesIO

from paho.mqtt.client import Client
from pydub import AudioSegment

audio_file = {}
frame_rate = 16000


def audio_callback(client, userdata, message):
    global audio_file, frame_rate
    topic_parts = message.topic.split("/")
    if topic_parts[3] == "audioFrame":
        site_id = topic_parts[2]
        if site_id not in audio_file:
            audio_file[site_id] = AudioSegment.empty()
        audio_file[site_id] += AudioSegment.from_wav(BytesIO(message.payload))
        if audio_file[site_id].frame_count() > (frame_rate * 10):
            audio_file[site_id] = audio_file[site_id].get_sample_slice(max(int(audio_file[site_id].frame_count() - frame_rate * 2), 0), int(audio_file[site_id].frame_count()))


def save_wakeword(client, userdata, message):
    global audio_file, frame_rate
    time.sleep(10)
    topic_parts = message.topic.split("/")
    wake_word = topic_parts[2]
    site_id = json.loads(message.payload)["siteId"]
    filename = wake_word + "_" + str(datetime.datetime.now().timestamp()) + ".wav"
    folder = os.path.join(wake_word, site_id)
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, filename)
    audio_file[site_id] = audio_file[site_id].get_sample_slice(
        max(int(audio_file[site_id].frame_count() - 2 * frame_rate), 0), int(audio_file[site_id].frame_count() - 1000))
    audio_file[site_id].export(file_path, format="wav")
    print(f"Recorded audio: {file_path}".format(file_path=file_path))
    audio_file[site_id] = audio_file[site_id].empty()


config = configparser.ConfigParser()
config.read('config.ini')
client = config["mqtt"]["client"]
server = config["mqtt"]["server"]
port = config["mqtt"].getint("port")
user = config["mqtt"]["user"]
password = config["mqtt"]["password"]

mqtt_client = Client(config["mqtt"]["client"])
mqtt_client.username_pw_set(config["mqtt"]["user"], config["mqtt"]["password"])
mqtt_client.on_message = audio_callback
mqtt_client.connect(config["mqtt"]["server"], config["mqtt"].getint("port"))
mqtt_client.subscribe("hermes/audioServer/+/audioFrame")
mqtt_client.subscribe("hermes/hotword/+/detected")
mqtt_client.message_callback_add("hermes/hotword/#", save_wakeword)
mqtt_client.loop_forever()
