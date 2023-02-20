#resource catalog
import json
import datetime
import requests
import cherrypy
from ResourceCatalog import *

class ManagerResource():

    exposed = True
    # mqtt-info
    # create a Catalog

    def __init__(self,  sensors, settings, home_settings):
        self.saved_file = sensors
        with open(self.saved_file, "w") as myfile:
           myfile.write("{}")
        self.sensors = json.load(open(self.saved_file))  # resource catalog

        self.settings = settings
        self.home_settings = home_settings
        putstring = "http://" + str(self.home_settings["ip_address"]) + ":" + str(self.home_settings["ip_port"])
        print(putstring)
        requests.put(putstring, json.dumps(self.settings))
        print("POSTING INFORMATION TO THE SERVICE CATALOG\n")
        self.RM = ResourceCatalog(self.sensors)
    def GET(self, *uri, **params):
        if len(uri) == 1 and len(params) < 2:
            if uri[0] == 'all':
                return self.RM.listSensors()

            elif uri[0] == 'sensor':
                output = self.RM.sensorByID(params['ID_sensor'])
                if output == {}:
                    raise cherrypy.HTTPError(400, 'sensor not found')
                return output
            else:
                raise cherrypy.HTTPError(400,
                                         'The URI: ' + {uri[0]} + ' is incorrect: expected values are'+
                                                                  ' all or sensor')

        else:
            raise cherrypy.HTTPError(400, 'incorrect URI or PARAMETERS URI' + {len(uri)} + 'PAR {len(parameters)}')

    def POST(self, *uri, **params):
        if len(uri) == 1:
            body = cherrypy.request.body.read()
            json_body = json.loads(body)
            if (uri[0] == 'sensor'):
                print("SENSOR INFORMATION RECEIVED (post)!\n")
                print("body=", json_body, "\n")
                if self.RM.sensorByTopic(json_body) != {}:
                    raise cherrypy.HTTPError(400, 'The sensor is already present!')
                self.sensors = self.RM.addSensor(json_body)
                self.sensors = json.loads(self.sensors)

                print("SENSOR INFORMATION REGISTERED (post)!\n")
                with open(self.saved_file, "w") as f:
                    json.dump(self.sensors, f)

            else:
                raise cherrypy.HTTPError(400, 'invalid uri')

        else:
            raise cherrypy.HTTPError(400, 'incorrect URI or PARAMETERS')

    def PUT(self, *uri, **params):
        if len(uri) == 1:
            body = cherrypy.request.body.read()
            json_body = json.loads(body)
            if uri[0] == 'sensor':
                print("SENSOR INFORMATION RECEIVED (put)!\n")
                print("body=", json_body, "\n")

                if self.RM.sensorByID(json_body['ID_sensor']) != {}:
                    print("update??")
                    self.sensors = self.RM.updateSensor(json_body)
                    print("SENSOR INFORMATION UPDATED (put)!\n")
                else:
                    self.sensors = self.RM.addSensor(json_body)
                    print("SENSOR INFORMATION REGISTERED (put)!\n")
            if uri[0] == 'oxygen':
                print("MODIFIED OXYGEN FLOW")
                resource = json.load(open("ResourceCatalog_info.json"))
                for dev in resource:
                    for i in range(len(resource[dev])):
                        if resource[dev][i]['patient'] == json_body['patient']:
                            resource[dev][i]['oxygen_flow'] = json_body['oxygen_flow']
                            with open("ResourceCatalog_info.json", "w") as f:
                                json.dump(resource, f)
            else:
                raise cherrypy.HTTPError(400, 'invalid uri')

        else:
            raise cherrypy.HTTPError(400, 'incorrect URI or PARAMETERS')





if __name__ == "__main__":

    settings = json.load(open(sys.argv[1]))
    sensors = sys.argv[2]
    home_settings = json.load(open("HomeCatalog_settings.json"))

    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }

    cherrypy.tree.mount(ManagerResource(sensors, settings, home_settings), '/', conf)
    cherrypy.config.update(conf)
    cherrypy.config.update({'server.socket_host': settings['ip_address']})
    cherrypy.config.update({"server.socket_port": int(settings['ip_port'])})
    cherrypy.engine.start()
    cherrypy.engine.block()