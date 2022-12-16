import json
import time
import cherrypy
import datetime
import sys
import requests

#copia 5,1 catalog
class ResourceCatalog:   #non sono sicura che servano classi diverse
""" un catalog è una stanza, con una lista di sensori. Ogni catalog ha un paziente (informazione da passare al service catalog)
"""
    #ritornare informazioni su: lista sensori,
    def __init__(self):
        self.devices_list = []
        self.users_list = []

    # --------- DEVICES ---------

    def sensorByID(self, deviceID):

    def listSensors(self):
        return json.dumps(self.devices)


    def addSensor(self):

    def updateSensor(self, sensorID):



    def searchDeviceByDeviceID(self, deviceID):
        return [o.__dict__ for o in self.devices_list if o.deviceID == deviceID]

    def addDevice(self, endpoints, resources):
        # create a non-existing ID
        newID = None
        done = False
        while not done:
            already_existing = False
            ID = 'D' + str(random.randint(0, 100000))
            for i in self.devices_list:
                if i.deviceID == ID:
                    already_existing = True
            if not already_existing:
                done = True
                newID = ID
        # create a new device
        new_device = Device(newID, endpoints, resources)
        self.devices_list.append(new_device)
        return 0  # device created with success

    def updateDevice(self, deviceID, endpoints, resources):
        # search the device
        done = False
        for dev in self.devices_list:
            if dev.deviceID == deviceID:
                dev.updateEndpoints(endpoints)
                dev.updateResources(resources)
                done = True
        # return
        if done:
            return 0  # success
        else:
            return 1  # not success

    def returnAllDevices(self):
        json_to_return = []
        for dev in self.devices_list:
            json_to_return.append(dev.__dict__)
        return json_to_return
