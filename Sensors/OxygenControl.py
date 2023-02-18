import json
from MyMQTT import *
import time
import cherrypy
from datetime import datetime
import sys


class OxigenControl():  # THIS PROGRAM RECEIVES DATA VIA MQTT FROM THE SENSORS AND ACTS AS A SERVER FOR PROVIDING INFORMATION TO THE APPLICATIONS

    def __init__(self, baseTopic, broker, port):
        self.clientID = "oxigen_control"
        self.baseTopic = baseTopic
        self.value = 0
        self.client = MyMQTT(self.clientID, broker, port, self)

    def run(self):
        self.client.start()

    def end(self):
        self.client.stop()

    def follow(self, topic):
        self.client.mySubscribe(topic)

    def notify(self, topic, msg):
        payload = json.loads(msg)
        result = payload
        result_dict = json.loads(result)
        if result_dict["e"][0]['warning'] == 'min':
            if self.value < 5:
                self.value = self.value + 1
                print('Livello ossigeno erogato:' + str(self.value))
            else:
                print('Ossigeno già erogato al livello massimo')
        if resutl_dict["e"][0]['warning'] == 'max' or result_dict["e"][0]['warning'] == 'max_good':
            if self.value > 0:
                self.value = self.value - 1
                print('Livello ossigeno erogato:' + str(self.value))
            else:
                print('Ossigeno già erogato al livello minimo')




if __name__ == '__main__':
    config = json.load(open(sys.argv[1]))  # oxigen control settings
    Home_info = json.load(open("HomeCatalog_settings.json"))
    coll = OxigenControl(Home_info["base_topic"], config["broker"], config["broker_port"])
    coll.run()
    coll.client.unsubscribe()
    result = coll.follow(coll.baseTopic + '/emergency/oxygen')
    cherrypy.engine.block()
    coll.end()
