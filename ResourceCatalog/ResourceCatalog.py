import json
import time
import cherrypy
import datetime
import sys
import requests


# copia 5,1 catalog
class ResourceCatalog():  # non sono sicura che servano classi diverse
    """
un catalog è una stanza, con una lista di sensori. Ogni catalog ha un paziente (informazione da passare al service catalog)
"""

    # ritornare informazioni su: lista sensori,
    def __init__(self, devices):
        self.sensors = devices  # mettilo come un dizionario!!!!

    # --------- DEVICES ---------

    def sensorByID(self, sensorID):
        print("sensor_list")
        print(self.sensors)
        for dev in self.sensors:

            if dev['ID_sensor'] == sensorID:  # CAMBIARE 'sensor_id' in ID_sensor
                return json.dumps(dev)
        return {}

    def sensorByTopic(self, sensor):
        for dev in self.sensors:
            for i in range(len(self.sensors[dev])):
                if self.sensors[dev][i]['communication']['complete_topic'] == sensor['communication'][
                    'complete_topic']:  # CAMBIARE 'sensor_id' in ID_sensor
                    return json.dumps(self.sensors[dev][i]["ID_sensor"])
        return {}

    def listSensors(self):
        return json.dumps(self.sensors)

    def addSensor(self, sensor):
        sensor['insert-timestamp'] = time.time()
        if sensor['patient'] not in self.sensors.keys():
            self.sensors[sensor['patient']] = []
        self.sensors[sensor['patient']].append(sensor)
        '''
        if isinstance(sensor['sensortype'], list):
            for t in sensor['sensortype']:
                types.append(t)
        else:
            types.append(sensor['sensortype'])

        for t in types:
            if t not in self.sensors.keys():
                self.sensors[t] = []
            self.sensors[t].append(sensor)
        '''
        return json.dumps(self.sensors)

    def updateSensor(self, sensor):
        if len(self.sensors) == 0:
            return {}
        for dev in self.sensors:
            if dev['ID_sensor'] == sensor['ID_sensor']:
                dev['communication'] = sensor['communication']
                break
        return json.dumps(self.sensors)
