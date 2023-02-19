import json
from MyMQTT import *
import time
import cherrypy
from datetime import datetime
import sys
import requests

class OxigenControl():  # THIS PROGRAM RECEIVES DATA VIA MQTT FROM THE SENSORS AND ACTS AS A SERVER FOR PROVIDING INFORMATION TO THE APPLICATIONS

    def __init__(self, baseTopic, Home_catalog_settings, broker, port):
        self.clientID = "oxigen_control"
        topic = baseTopic.split("/")
        self.baseTopic = topic[0]
        self.Home_catalog_settings = Home_catalog_settings
        self.client = MyMQTT(self.clientID, broker, port, self)
        Home_get_string = "http://" + self.Home_catalog_settings["ip_address"] + ":" + str(
            self.Home_catalog_settings["ip_port"]) + "/resource_catalogs"
        rc_info = json.loads(requests.get(Home_get_string).text)
        self.rooms = []
        request_string = "http://" + rc_info["ip_address"] + ":" + str(rc_info["ip_port"]) + "/sensor?ID_sensor=sensor_oxygen"
        patients = json.loads(requests.get(request_string).text)
        for patient in patients:
            self.rooms.append({"room_name": patient["patient"], "oxygen_flow": patient["oxygen_flow"]})
        self.put = 'http://' + str(rc_info["ip_address"]) + ':' + str(rc_info["ip_port"]) + '/oxygen'


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
        for room in self.rooms:
            if room['room_name'] == result_dict["e"][0]['patient']:
                if result_dict["e"][0]['warning'] == 'min':
                    if room['oxygen_flow'] < 5:
                        room['oxygen_flow'] = room['oxygen_flow'] + 1
                        print('Level of oxigen flow delivered: ' + str(room['oxygen_flow']) + ' to the patient ' + room['room_name'])
                        message = {
                            'patient': room['room_name'],
                            'oxygen_flow': room['oxygen_flow']
                        }
                        requests.put(self.put, json.dumps(message))
                    else:
                        print('Oxygen flow already delivered at maximum level to the patient ' + room['room_name'])
                if result_dict["e"][0]['warning'] == 'max' or result_dict["e"][0]['warning'] == 'max_good':
                    if room['oxygen_flow'] > 0:
                        room['oxygen_flow'] = room['oxygen_flow'] - 1
                        print('Level of oxigen flow delivered: ' + str(room['oxygen_flow']) + ' to the patient ' + room['room_name'])
                        message = {
                            'patient': room['room_name'],
                            'oxygen_flow': room['oxygen_flow']
                        }
                        requests.put(self.put, json.dumps(message))
                    else:
                        print('Oxygen flow already delivered at minimum level to the patient ' + room['room_name'])




if __name__ == '__main__':
    config = json.load(open(sys.argv[1]))  # oxigen control settings
    Home_info = json.load(open("HomeCatalog_settings.json"))
    coll = OxigenControl(Home_info["base_topic"], Home_info, config["broker"], config["broker_port"])
    coll.run()
    coll.client.unsubscribe()
    coll.follow(coll.baseTopic + '/emergency/oxygen')
    cherrypy.engine.block()
    coll.end()
