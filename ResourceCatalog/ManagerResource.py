#resource catalog
import json
import datetime
import requests
import cherrypy
from ResourceCatalog import *

class ManagerResource():
    """
    devices = devices_file
    settings = json of setting_file
    home_settings: json of service_file
    """
    exposed = True
    # mqtt-info
    # create a Catalog

    def __init__(self,  sensors, settings, home_settings):
        #self.usersFile = users_file
        # self.users=json.load(open(self.usersFile)) #for future usage
        self.saved_file = sensors
        with open(self.saved_file, "w") as myfile:
            myfile.write("[]")
        self.sensors = json.load(open(self.saved_file))  # resource catalog

        self.settings = settings
        self.home_settings = home_settings
        poststring = "http://" + str(self.home_settings["ip_address"]) + ":" + str(self.home_settings["ip_port"])
        requests.put(poststring, json.dumps(self.settings))
        print("POSTING INFORMATION TO THE SERVICE CATALOG\n")
        self.RM = ResourceCatalog(self.sensors)
    def GET(self, *uri, **params): #copiare da 5.1 server
        if len(uri) == 1 and len(params) < 2:
            if uri[0] == 'all':  #cosa esce da questa chiamata?
                return self.RM.listSensors()
                #???????????????????????' usare users?
            # elif uri[0]=='allusers':   #FOR FUTURE USE
            #    return self.viewAllUsers()
            # elif uri[0]=='user':
            #    output=self.searchUserByUserID(parameters['user_id'])
            #    if output=={}:
            #        raise cherrypy.HTTPError(400, 'user not found')
            #    return output
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
                print("SENSOR INFORMATION RECEIVED!\n")
                print("body=", json_body, "\n")
                if self.RM.sensorByID(json_body['ID_sensor']) != {}:
                    raise cherrypy.HTTPError(400, 'The sensor is already present!')
                # print(json_body)
                self.sensors = self.RM.addSensor(json_body)
                print("SENSOR INFORMATION REGISTERED!\n")
                with open(self.saved_file, "w") as f:
                    json.dump(self.sensors, f)

            else:
                raise cherrypy.HTTPError(400, 'invalid uri')
            '''
            elif (uri[0] == 'user'): #?????????????????
                if self.searchUserByUserID(json_body['user_id']) != {}:
                    raise cherrypy.HTTPError(400, 'user already present')
                self.insertUser(json_body)
                self.sensors = json.load(open(self.devicesFile))
            '''
        else:
            raise cherrypy.HTTPError(400, 'incorrect URI or PARAMETERS')

    def PUT(self, *uri, **params):
        if len(uri) == 1:
            body = cherrypy.request.body.read()
            json_body = json.loads(body)
            if uri[0] == 'sensor':
                print("SENSOR INFORMATION RECEIVED!\n")
                print("body=", json_body, "\n")
                if self.RM.sensorByID(json_body['ID_sensor']) != {}:
                    self.sensors = self.RM.updateSensor(json_body)
                    print("SENSOR INFORMATION UPDATED!\n")
                else:
                    self.sensors = self.RM.addSensor(json_body)
                    print("SENSOR INFORMATION REGISTERED!\n")

            else:
                raise cherrypy.HTTPError(400, 'invalid uri')

        else:
            raise cherrypy.HTTPError(400, 'incorrect URI or PARAMETERS')





if __name__ == "__main__":

    #users_file = "res_cat_users_1.json"  # for future use, can be modified to be obtained through argv
    settings = json.load(open(sys.argv[1]))   #resource catalog setting
    sensors = sys.argv[2] #resource catalog device specifico
    home_settings = json.load(open("HomeCatalog_settings.json"))

    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }

    #cherrypy.tree.mount(ResourceCatalogManager(users_file, devices_file, service_file, setting_file), '/', conf)
    cherrypy.tree.mount(ManagerResource(sensors, settings, home_settings), '/', conf)
    cherrypy.config.update(conf)
    cherrypy.config.update({'server.socket_host': settings['ip_address']})
    cherrypy.config.update({"server.socket_port": int(settings['ip_port'])})
    cherrypy.engine.start()
    ''' penso che sia usato per cancellare dei device non aggiornati
    rcm = ResourceCatalogManager(sensors, setting_device, home_settings)
    while 1:
        rcm.removeDevices()
        time.sleep(120)
    
    '''
    cherrypy.engine.block()