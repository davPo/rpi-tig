#!/usr/bin/env python

import os, sys, time,logging,random
import paho.mqtt.client as mqtt  

class MqttClient():
    def __init__(self, address, name, username='', password=''):
        self.address = address
        self.name = name
        self.client = mqtt.Client(name)    #create new instance 
        if(username != ""):
            self.client.username_pw_set(username,password)
        self.client.connected_flag = False #create flag in class
        self.client.on_connect=self.on_connect  #bind call back function
        self.client.on_publish=self.on_publish #assing function to call back

    def connect(self):
        self.client.loop_start()
        logging.info("Connecting to broker %s"%(self.address))
        self.client.connect(self.address)      #connect to broker
        while not self.client.connected_flag: #wait in loop
            #print("In wait loop")
            time.sleep(1)
        #print("in Main Loop")
        self.client.loop_stop()    #Stop loop 
        
    def disconnect(self):
        self.client.disconnect() # disconnect
        logging.info("Disconnected")

    def publish(self, topic, data):
        ret=self.client.publish(topic, data)

    def on_connect(self, client, userdata, flags, rc):
        if rc==0:
            client.connected_flag=True #set flag
            logging.info('Connected')  
        else:
            logging.error("Bad connection Returned code=",rc)  

    def on_publish(self,client,userdata,result):  #create function for callback
        logging.info('Data published')

import numpy as np
import sounddevice as sd
import argparse

# Use alsamixer to setup microphone gain

class Microphone():
    def __init__(self):
      self.device = sd.default.device
      self.channels = 1
      self.fs = 44100
      self.samples = None

    def list_devices(self):
        r = sd.query_devices()
        print(r)

    def set_device(self,device):
        #sd.default.device = device
        try:
            self.device = device
            device_info  = sd.query_devices(device, 'input') 
            self.fs = device_info['default_samplerate']
        except ValueError:
            logging.error("Not an input device")  
            print("Not an input device")
            exit()

    def record(self,time_s=10):
        self.samples = sd.rec(int(time_s * self.fs), device=self.device, samplerate=self.fs, channels=self.channels)
        print ("Collecting values for %d seconds..."%(time_s))
        sd.wait()

    def get_maximum_value(self):
        if self.samples.any():
            return np.max(self.samples)
        else:
            return 0

    def get_rms_value(self):
        if self.samples.any():
            rms = np.sqrt(np.mean(self.samples**2))
            return rms
        else:
            return 0

    def get_samples(self):
        return self.samples

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

if __name__ == '__main__':
    # Parsing Args
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
    args, remaining = parser.parse_known_args()
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)
    parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
    parser.add_argument(
    '-t', '--time', type=int, default=1,
    help='acquisition time (default: %(default)s s)')
    args = parser.parse_args(remaining)
    # Logger
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)
    # Mic test
    mic = Microphone()
    mic.set_device(args.device)
    mic.record(args.time)
    rms = mic.get_rms_value()
    max = mic.get_maximum_value() 
    print("Done : RMS = %f Max = %f"%(rms, max ))

   # print(mic.get_samples())
   # mic.list_devices()
    # Mqtt publish
    mqttclient = MqttClient('127.0.0.1', 'NoiseMon')
    mqttclient.connect()
    # Note : set telegraf inputs.mqtt consumer as value / float
    mqttclient.publish("sensors/noise/max", float(max))
    mqttclient.publish("sensors/noise/rms", float(rms))
    mqttclient.disconnect()
