import json
import time
import cherrypy
import datetime
import sys
import requests

#copia 5,1 catalog
class ResourceCatalog():   #non sono sicura che servano classi diverse
    """
un catalog è una stanza, con una lista di sensori. Ogni catalog ha un paziente (informazione da passare al service catalog)
"""
    #ritornare informazioni su: lista sensori,
    def __init__(self, devices):
        self.sensors_list = devices

    # --------- DEVICES ---------

    def sensorByID(self, sensorID):
        for dev in self.sensors_list:
            if dev['ID_sensor'] == sensorID:  #CAMBIARE 'sensor_id' in ID_sensor
                return json.dumps(dev)
        return {}

    def listSensors(self):
        return json.dumps(self.sensors_list)

    def addSensor(self, sensor):
        sensor['insert-timestamp'] = time.time()
        self.sensors_list.append(sensor)
        return  json.dumps(self.sensors_list)

    def updateSensor(self, sensor):
        if len(self.sensors_list) == 0:
            return {}
        for dev in self.sensors_list:
            if dev['ID_sensor'] == sensor['ID_sensor']:
                dev['comunication'] = sensor['comunication']
                dev['available_resources'] = sensor['available_resources'] #non lo trovo
                dev['insert-timestamp'] = time.time()
                break
        return  json.dumps(self.sensors_list)




