import time
import os
import logging

#  An Example Reading from /sys/bus/w1/devices/<ds18b20-id>/w1_slave
#  a6 01 4b 46 7f ff 0c 10 5c : crc=5c YES
#  a6 01 4b 46 7f ff 0c 10 5c t=26375

import RPi.GPIO as GPIO
import paho.mqtt.client as mqttClient
import json

#  Set Pull-up mode on GPIO14 first.
GPIO_PIN_NUMBER=4
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN_NUMBER, GPIO.IN, pull_up_down=GPIO.PUD_UP)

id_to_name = {'28-3c01d075ff96':"supply-temp", '28-xxx':"return-temp", '28-xx':"tank-temp"}

def ds18b20_read_sensors():
    rtn = {}
    w1_devices = os.listdir("/sys/bus/w1/devices/")
    for deviceid in w1_devices:
        rtn[deviceid] = {}
        rtn[deviceid]['temp_c'] = None
        device_data_file = "/sys/bus/w1/devices/" + deviceid + "/w1_slave"
        if os.path.isfile(device_data_file):
            try:
                f = open(device_data_file, "r")
                data = f.read()
                f.close()
                if "YES" in data:
                    (discard, sep, reading) = data.partition(' t=')
                    rtn[deviceid]['temp_c'] = float(reading) / float(1000.0)
                else:
                    rtn[deviceid]['error'] = 'No YES flag: bad data.'
            except Exception as e:
                rtn[deviceid]['error'] = 'Exception during file parsing: ' + str(e)
        else:
            rtn[deviceid]['error'] = 'w1_slave file not found.'
    return rtn


class MqttSender:
    def __init__(self, broker_address="localhost"):
        self.connected = False
        self.client = mqttClient.Client("1wire")
        # set username and password to mqtt
        self.client.on_connect = self.on_connect
        self.client.connect(broker_address)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to mqtt broker")
            self.connected = True
        else:
            logging.error("Did not connect to mqtt broker")

    def send(self, id, value):
        if self.connected:
            name = id
            if id in id_to_name:
                name = id_to_name[id]
            data = json.dumps({'id':id, 'name':name, 'value':value})
            logging.debug(f'sending: temperature/water/{id} {data}')
            self.client.publish(f'temperature/water/{id}', data)
        else:
            logging.error("Not connected to mqtt server")


# logging.basicConfig(level=logging.DEBUG)
mqtt = MqttSender()


while True:
    temp_readings = ds18b20_read_sensors()
    for t in temp_readings:
        if 'error' not in temp_readings[t]:
            logging.info(u"Device id '%s' reads %.3f +/- 0.5 °C" % (t, temp_readings[t]['temp_c']))
            mqtt.send(t, temp_readings[t]['temp_c'])

        time.sleep(1.0)

