from MyMQTT import *
import json
import random
import requests
import sys
import time


class SensorComunication:

    def __init__(self, broker, clientID, port, sensorID, sensormeasure, sensortype, topic):
        self.clientID = clientID
        self.sensortype = sensortype
        self.sensorID = sensorID
        self.sensormeasure = sensormeasure
        self.topic = topic
        self.client = MyMQTT(self.sensorID, broker, port, None)

        self.__message = {
            'bn': self.topic,
            'e': [
                {
                    'type': self.sensortype,
                    'unit': self.sensormeasure,
                    'patient': '',
                    'value': '',
                    'time': ''
                }
            ]
        }

    def start(self):
        self.client.start()

    def stop(self):
        self.client.stop()

    def publish(self, value, patient):
        message = self.__message
        message['e'][0]['patient'] = patient
        message['e'][0]['value'] = value
        message['e'][0]['time'] = str(time.time())
        self.client.myPublish(self.topic, json.dumps(message))
        print("Published!\n" + json.dumps(message) + "\n")


def RegisterSensor(sensor_settings, home_settings):  #how to register the sensor on the resource catalog
    with open(sensor_settings, "r") as file1:
        conf_sensor = json.loads(file1.read())

    with open(home_settings, "r") as file2:
        conf_home = json.loads(file2.read())
    request = 'http://' + str(conf_home['ip_address']) + ':' + str(conf_home[ 'ip_port']) + '/patients'
    ListOfPatients = requests.get(request)
    print("Connection with home catalog: OK\n")
    names = ListOfPatients.json()
    check_name = False
    while check_name == False:
        print("List of patients:\n ")
        for i in range(len(names['names'])):
            print("Patient "+str(i+1)+" : "+names['names'][i]+"\n")
        index_patient = input("Which patient do you want to check? Insert the number please ")
        if isinstance(index_patient, str) and index_patient.isnumeric():
            int_index = int(index_patient)
            if (int_index-1) in range(len(names['names'])):
                patient = names['names'][int(index_patient) - 1]
                check_name = True
            else:
                print("Sorry, you have give the wrong input, try again!")
        else:
            print("Sorry, you have give the wrong input, you have to write only the number corresponding to the patient!")

    request = 'http://' + str(conf_home['ip_address']) + ':' + str(conf_home['ip_port']) + '/info_room?patient=' + patient
    ResourceCatalog = requests.get(request)
    rc = json.loads(ResourceCatalog.text)
    print("Information on patient " + rc['patient'] + " received (from resource catalog)\n")  # PRINT FOR DEMO #modifica string

    if rc == 0:
        print('No record for this patient')
        return 'Patient not found'
    else:
        post = 'http://' + str(rc["ip_address"]) + ':' + str(rc["ip_port"]) + '/sensor'
        request = 'http://' + str(conf_home['ip_address']) + ':' + str(conf_home['ip_port']) + '/base_topic'
        ServiceTopic = requests.get(request)
        ServiceTopic = json.loads(ServiceTopic.text)



        CompleteTopic = ServiceTopic + '/' +rc["base_topic"] + '/' + conf_sensor['sensor_type'][0] + '/' + conf_sensor["ID_sensor"]
        body_dic = {
            "sensortype": conf_sensor['sensor_type'][0],
            "ID_sensor": conf_sensor['ID_sensor'],
            "patient": rc["patient"],
            "measure": conf_sensor["measure"],
            "oxygen_flow": 0,
            "communication": {
                "basetopic": ServiceTopic + '/' + rc["base_topic"],
                "complete_topic": CompleteTopic,
                "broker": rc["broker"],
                "port": rc["broker_port"]
            }
        }

        requests.post(post, json.dumps(body_dic))
        print("The patient has been registered on the resource catalog\n")

        Result_Dict = {
            "sensortype": conf_sensor["sensor_type"][0],
            "clientID": rc["base_topic"],
            "sensorID": conf_sensor["ID_sensor"],
            "topic": CompleteTopic,
            "measure": conf_sensor["measure"],
            "broker": rc["broker"],
            "port": int(rc["broker_port"]),
            "patient": rc["patient"]
        }

        return Result_Dict


if __name__ == "__main__":
    dict = RegisterSensor(sys.argv[1], "HomeCatalog_settings.json")
    while dict == 'Patient not found':
        dict = RegisterSensor(sys.argv[1], "HomeCatalog_settings.json")

    Sensor= SensorComunication(dict['broker'], dict['clientID'], int(dict['port']), dict['sensorID'], dict['measure'], dict['sensortype'], dict['topic'])
    Sensor.start()

    vect = [98, 97, 97, 97, 97, 96, 95, 95, 95, 96, 97, 98, 98, 98, 99, 99, 98, 97, 96, 96, 95, 94, 93, 93, 93, 92, 92, 91, 91, 92, 92, 92, 93, 94, 94, 95, 95, 95, 96, 96, 95, 96, 96, 96, 97]
    while 1:
        for i in vect:
            Oxygen = i
            #Oxygen = Oxygen + random.randint(-2, 2) #SIMULATED SENSOR
            print(Oxygen, dict['patient'])
            Sensor.publish(Oxygen, dict['patient'])
            time.sleep(5)

