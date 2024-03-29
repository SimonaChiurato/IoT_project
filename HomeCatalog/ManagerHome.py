#home catalog
import json
import cherrypy
from HomeCatalog import *

class ManagerHome(object):
    exposed = True
    CM = HomeCatalog()
    # mqtt-info
    def __init__(self):
        self.settings=json.load(open("HomeCatalog_settings.json"))


    def GET(self, *uri, **params):
        if len(uri) == 1:
            if uri[0] == 'resource_catalogs':
                self.settings = json.load(open("HomeCatalog_settings.json"))
                return json.dumps(self.settings["resource_catalogs"])

            elif uri[0] == 'patients':
                result = self.CM.returnAllPatients()
                return json.dumps(result)

            elif uri[0] == 'info_room':
                results = self.CM.searchPatient(params)
                return json.dumps(results)

            elif uri[0] == 'broker':
                temp = {'broker': self.settings['broker'], 'port': self.settings['broker_port']}
                return json.dumps(temp)

            elif uri[0] == 'base_topic':
                return json.dumps(self.settings["base_topic"])
        else:
            error_string = "incorrect URI or PARAMETERS URI"+str(uri)+" lenght"+str(len(uri))
            raise cherrypy.HTTPError(400, error_string)

    def POST(self, *uri):
        if len(uri) == 0:
            body = cherrypy.request.body.read()
            print("POST RECEIVED WITH BODY:", body)
            json_body = json.loads(body)
            self.CM.newResCat(json_body)
        else:
            error_string = "incorrect URI or PARAMETERS" + {len(uri)}
            raise cherrypy.HTTPError(400, error_string)


    def PUT(self, *uri):
        if len(uri) == 0:
            body = cherrypy.request.body.read()
            print("PUT RECEIVED WITH BODY:", body)
            json_body = json.loads(body)
            result = self.CM.updateResCat(json_body)
            with open("HomeCatalog_settings.json", "w") as f:
                json.dump(result, f, indent=4)
        else:
            error_string = "incorrect URI or PARAMETERS" + {len(uri)}
            raise cherrypy.HTTPError(400, error_string)

if __name__=="__main__":
    service_settings=json.load(open("HomeCatalog_settings.json"))
    conf={
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }
    cherrypy.tree.mount(ManagerHome(),'/', conf)
    cherrypy.config.update(conf)
    cherrypy.config.update({'server.socket_host':service_settings['ip_address']})
    cherrypy.config.update({"server.socket_port":service_settings['ip_port']})  #qui loro hanno una funzione
    cherrypy.engine.start()
    cherrypy.engine.block()