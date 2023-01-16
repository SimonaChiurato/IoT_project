import json
import requests
import time
import pygame
import cherrypy
import sys


class TemperatureServer:
    exposed = True

    def POST(self):  # RECEIVING THE MESSAGE FROM SENSOR TEMPERATURE IN ORDER TO MAKE SOMETHING
        body = json.loads(cherrypy.request.body.read())
        if body > 13:
            print ("Fa freddo, cerca dove mandare un allarme oppure scegli un azione da fare")
        else:
            print("Fa troppo freddooooo")
        time.sleep(2)


def registration(sensor_settings, home_settings):  # IN ORDER TO REGISTER ON THE RESOURCE CATALOG
    with open(sensor_settings, "r") as f1:
        conf_sensor = json.loads(f1.read())

    with open(home_settings, "r") as f2:
        conf_home = json.loads(f2.read())
    requeststring = 'http://' + str(conf_home['ip_address']) + ':' + str(conf_home[
        'ip_port']) + '/patients'    #ci siamo collegati al topic che ci restituisce la lista di nomi dei pazienti
    r = requests.get(requeststring)
    print("INFORMATION FROM SERVICE CATALOG RECEIVED!\n") #modifica
    names= r.json()
    print("List of patients:\n ") #\n??
    for i in range(len(names['names'])):
        print("Patient "+str(i+1)+" : "+names['names'][i]+"\n")
    index_patient = input("Which patient do you want to control? Insert the number please ")
    patient = names['names'][int(index_patient)-1]
    requeststring = 'http://' + str(conf_home['ip_address']) + ':' + str(conf_home[
        'ip_port']) + '/info_room?patient=' + patient
    r = requests.get(requeststring)
    print("INFORMATION OF RESOURCE CATALOG (room) RECEIVED!\n")  # PRINT FOR DEMO #modifica string

    rc = json.loads(r.text)
    if rc == 0:  #controllare cosa restituisce da manager home info_room
        print('Patient not found')
        return 'Patient not found'
    else:

        rc_ip = rc["ip_address"]
        rc_port = rc["ip_port"]
        poststring = 'http://' + str(rc_ip) + ':' + str(rc_port) + '/sensor'
        rc_basetopic = rc["base_topic"]
        rc_broker = rc["broker"]
        rc_port = rc["broker_port"]

        sensor_model = conf_sensor["sensor_model"]

        requeststring = 'http://' + str(conf_home['ip_address']) + ':' + str(conf_home[
            'ip_port']) + '/base_topic'
        sbt = requests.get(requeststring)

        service_b_t = json.loads(sbt.text)
        topic = []
        body = []
        index = 0
        for i in conf_sensor["sensor_type"]:
            print(i)
            topic.append(service_b_t + '/' + rc_basetopic + '/' + i + '/' + conf_sensor["ID_sensor"])
            body_dic = {
                "ID_sensor": conf_sensor['ID_sensor'],
                "sensor_type": conf_sensor['sensor_type'],
                "patient": rc["patient"],
                "measure": conf_sensor["measure"][index],
                "end-points": {
                    "basetopic": service_b_t + '/' + rc_basetopic,
                    "complete_topic": topic,
                    "broker": rc["broker"],
                    "port": rc["broker_port"]
                }
            }
            body.append(body_dic)
            requests.post(poststring, json.dumps(body[index]))
            print("REGISTRATION TO RESOURCE CATALOG (room) DONE!\n")  # PRINT FOR DEMO
        return 'Patient found'

if __name__ == "__main__":

    config = json.load(open(sys.argv[1]))
    result = registration(sys.argv[1], "service_catalog_info.json")
    while result == 'Patient not found':
        result = registration(sys.argv[1], "service_catalog_info.json")

    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }
    cherrypy.tree.mount(TemperatureServer(), '/', conf)
    cherrypy.config.update(conf)
    cherrypy.config.update({"server.socket_host": config["server_ip"]})
    cherrypy.config.update({"server.socket_port": config["server_port"]})
    cherrypy.engine.start()