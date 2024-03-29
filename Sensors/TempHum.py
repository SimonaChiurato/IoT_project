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
    request = 'http://' + str(conf_home['ip_address']) + ':' + str(conf_home[
        'ip_port']) + '/patients'
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
    print(rc)
    print("Information on patient " + rc['patient'] + " received (from resource catalog)\n")

    if rc == 0:
        print('No record for this patient')
        return 'Patient not found'
    else:
        post = 'http://' + str(rc["ip_address"]) + ':' + str(rc["ip_port"]) + '/sensor'
        request = 'http://' + str(conf_home['ip_address']) + ':' + str(conf_home['ip_port']) + '/base_topic'
        ServiceTopic = requests.get(request)
        ServiceTopic = json.loads(ServiceTopic.text)
        CompleteTopic = []
        for i in conf_sensor["sensor_type"]:
            print(i)
            CompleteTopic.append(ServiceTopic + '/' + rc["base_topic"] + '/' + i + '/' + conf_sensor["ID_sensor"])
        body_dic = {
            "sensortype": conf_sensor['sensor_type'],
            "ID_sensor": conf_sensor['ID_sensor'],
            "patient": rc["patient"],
            "measure": conf_sensor["measure"],
            "communication": {
                "basetopic": ServiceTopic + '/' + rc["base_topic"],
                "complete_topic": CompleteTopic,
                "broker": rc["broker"],
                "port": rc["broker_port"]
            }
        }
        requests.post(post, json.dumps(body_dic))
        print("The patient has been registered on the resource catalog\n")  # PRINT FOR DEMO

        Result_Dict = {
            "sensortype": conf_sensor["sensor_type"],
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
    sensor_settings = json.load(open(sys.argv[1]))
    dict = RegisterSensor(sys.argv[1], "HomeCatalog_settings.json")
    while dict == 'Patient not found':
        dict = RegisterSensor(sys.argv[1], "HomeCatalog_settings.json")

    value_sensortype = 0  #take the value regarding the right type of sensor (first temperature, then humidity)
    Sensor = []
    for i in dict['sensortype']:
        Sensor.append(SensorComunication(dict['broker'], dict['clientID'], int(dict['port']), dict['sensorID'], dict['measure'][value_sensortype], i, dict['topic'][value_sensortype]))
        Sensor[value_sensortype].start()
        value_sensortype = value_sensortype + 1

    vect = [20.2, 20.1, 20.0, 20.0, 20.1, 20.1, 20.1, 20.2, 20.2, 20.3, 20.3, 20.3, 20.3, 20.4, 20.5, 20.6, 20.6, 20.7, 20.8, 20.9, 21.0, 21.2, 21.2, 21.3, 21.5, 21.6, 21.9, 22.1, 21.8, 21.5, 21.3, 21.0, 20.8, 20.5, 20.2, 20.0, 19.8, 19.5, 19.3, 19.2, 19.0, 19.0, 18.9, 19.0, 19.2]
    vectt = [50, 51, 50, 52, 52, 53, 54, 53, 52, 53, 54, 55, 56, 55, 55, 55, 54, 54, 55, 56, 56, 56, 57, 58, 58, 58, 58, 59, 59, 59, 59, 60, 60, 61, 61, 60, 59, 59, 58, 58, 57, 56, 55, 55, 55]

    while 1:
        for i in range(len(vect)):
            Temperature = vect[i]
            Humidity = vectt[i]
            #Temperature = Temperature + random.randint(-1,1) #SIMULATED SENSOR
            print(Temperature)
            Sensor[0].publish(Temperature, dict['patient'])
            #Humidity = Humidity + random.randint(-20,20) #SIMULATED SENSOR
            print(Humidity )
            Sensor[1].publish(Humidity, dict['patient'])
            time.sleep(5)

