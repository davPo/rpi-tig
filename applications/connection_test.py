#!/usr/bin/env python

import os, sys, time
import paho.mqtt.client as mqtt  #import the client1

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        print("connected OK")
    else:
        print("Bad connection Returned code=",rc)

def on_publish(client,userdata,result):  #create function for callback
    print("data published \n")
    pass

mqtt.Client.connected_flag=False#create flag in class
broker="127.0.0.1"
client = mqtt.Client("python_test")    #create new instance 
#client.username_pw_set(username="XXXXXX", password="XXXXXX")
client.on_connect=on_connect  #bind call back function
client.on_publish=on_publish #assing function to call back
client.loop_start()
print("Connecting to broker ",broker)
client.connect(broker)      #connect to broker
while not client.connected_flag: #wait in loop
    print("In wait loop")
    time.sleep(2)
print("in Main Loop")
client.loop_stop()    #Stop loop 

ret=client.publish("sensors/value", random.randint(1, 255))

#client.disconnect() # disconnect
