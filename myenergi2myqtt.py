#!/usr/bin/env python3 

import daemon
import lockfile

import paho.mqtt.client as mqtt

import yaml
import signal


import time
import os.path
import sys
from pprint import pprint

import myenergi

class MyEnergiDaemon:
    def __init__(self,cfg):
        self.mqtt_client = mqtt.Client()
        self.config = {}
        self.shutdown=False

        with open(cfg, 'r') as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        self.hub = myenergi.MyenergiHub(self.config)
        self.mqtt_client.connect(self.config["mqtt"]["host"],self.config["mqtt"]["port"], 60)

    def mqtt_on_connect(self):
        print("Connected with result code "+str(rc))

    def mqtt_on_message(self):
        print("Topic: "+msg.topic+"->"+str(msg.payload))

    def on_shutdown(self):
        print("Terminate")
        self.shutdown=True


    def do_daemon(self):

        while not self.shutdown: 
            self.hub.getStatus()

            self.mqtt_client.loop_start()

            for (serial) in self.hub.getZappis():
                self.mqtt_client.publish(f"myenergi/zappi/{serial}",self.hub.getZappi(serial).getJson())

            self.mqtt_client.loop_stop()

            time.sleep(self.config["myenergi"]["interval"])
        print("Shutdown")

            
    def on_shutdown(self):
        print("Shutdown")
        self.mqtt_client.disconnect()


mydaemon = MyEnergiDaemon(sys.argv[1])

# todo: use CLI 
foreground=True


if foreground == True:
    mydaemon.do_daemon()
else:
    #TODO: Not working with MQTT
    with daemon.DaemonContext(    
       signal_map={
               signal.SIGTERM:     mydaemon.on_shutdown(),
               signal.SIGTSTP:     mydaemon.on_shutdown(),
           }, 
       stderr=sys.stderr,
       stdout=sys.stdout,
       pidfile=lockfile.FileLock('myenergi.pid')):
           mydaemon.do_daemon()
