# rhasspy_save_wakeword

This is a small script that listens to the hermes/audioServer/+/audioFrame and hermes/hotword/+/detected mqtt topics and saves the audio it buffers from audioFrame after the wakeword was detected. 

The intended use is to collect wakeowrd samples (and wrongly detected wakewords) for custom model training.

Requirements are paho-mqtt and pydub. This was only tested on python 3.7
