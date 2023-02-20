import json
import time
import cherrypy
import datetime
import sys
import requests


# copia 5,1 catalog
class ResourceCatalog():

    def __init__(self, devices):
        self.sensors = devices

    def sensorByID(self, sensorID):
        #print(self.sensors)
        message =  []
        found = 0
        for dev in self.sensors:
            for i in range(len(self.sensors[dev])):
                if  self.sensors[dev][i]['ID_sensor'] == sensorID:
                    message.append(self.sensors[dev][i])
                    found = 1
        if found == 1:
            return json.dumps(message)
        return {}

    def sensorByTopic(self, sensor):
        for dev in self.sensors:
            for i in range(len(self.sensors[dev])):
                if self.sensors[dev][i]['communication']['complete_topic'] == sensor['communication'][
                    'complete_topic']:
                    return json.dumps(self.sensors[dev][i]["ID_sensor"])
        return {}

    def listSensors(self):
        return json.dumps(self.sensors)

    def addSensor(self, sensor):
        sensor['insert-timestamp'] = time.time()
        if sensor['patient'] not in self.sensors.keys():
            self.sensors[sensor['patient']] = []
        self.sensors[sensor['patient']].append(sensor)

        return json.dumps(self.sensors)

    def updateSensor(self, sensor):
        if len(self.sensors) == 0:
            return {}
        for dev in self.sensors:
            if dev['ID_sensor'] == sensor['ID_sensor']:
                dev['communication'] = sensor['communication']
                break
        return json.dumps(self.sensors)
