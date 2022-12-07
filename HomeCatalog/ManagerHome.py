#home catalog
import json
import cherrypy

#probabilmente 5.1 server
#controllare i json.dump
class ManagerHome(object):
    exposed = True
    # mqtt-info
    broker = "test.mosquitto.org"
    port = 1883
    ip_address = "192.168.1.208"
    ip_port = "8095"
    res_cat = json.load(open("resource_catalog_info.json"))  # quale resource catalog dovrei aprire?

    def GET(self, *uri, **params):

        if len(uri) == 1:

            if uri[0] == 'resource_catalog':
                return json.dumps(self.res_cat)

            elif uri[0] == 'owner':
                result = {"names": [self.res_cat["base_topic"] + ' ' + self.res_cat["owner"] + '\n'] }
                return json.dumps(result)

            elif uri[0] == 'room_info':
                results = [entry for entry in self.res_cat if (entry["base_topic"] == params["room"] and entry ["owner"] == params["owner"])]
                return json.dumps(results)

            elif uri[0] == 'broker':
                temp = {'broker': self.broker, 'port': self.port}
                return json.dumps(temp)


            elif uri[0] == 'base_topic':
                return json.dumps(self.res_cat["base_topic"])
        else:
            error_string = "incorrect URI or PARAMETERS URI" + {len(uri)} + "PAR" + {len(params)}
            raise cherrypy.HTTPError(400, error_string)

def POST(self, *uri):
    if len(uri) == 0:
        body = cherrypy.request.body.read()
        print("POST RECEIVED WITH BODY:", body)
        json_body = json.loads(body)
        already_existing = False
        for entry in self.res_cat:
            if entry["base_topic"] == json_body["base_topic"] and entry["owner"] == json_body["owner"]:
                already_existing = True
        if already_existing == False:
            self.res_cat.append(json_body)
            print(json_body)
            with open(self.res_cat, "w") as f:
                json.dump(self.res_cat, f)
            return "Resource catalog inserted with success"
        else:
            return "Resource catalog already existing"
    else:
        error_string = "incorrect URI or PARAMETERS" + {len(uri)}
        raise cherrypy.HTTPError(400, error_string)


def PUT(self, *uri):
    if len(uri) == 0:
        body = cherrypy.request.body.read()
        print("PUT RECEIVED WITH BODY:", body)
        json_body = json.loads(body)
        already_existing = False
        for entry in self.res_cat:
            if entry["base_topic"] == json_body["base_topic"] and entry["owner"] == json_body["owner"]:
                already_existing = True
                entry['base_topic'] == json_body["base_topic"]
                entry["broker"] == json_body["broker"]
                entry["broker_port"] == json_body["broker_port"]
                entry["base_topic"] == json_body["base_topic"]
                entry["ip_address"] == json_body["ip_address"]
                entry["ip_port"] == json_body["ip_port"]
                print(json_body)
            with open(self.res_cat, "w") as f:
                json.dump(self.res_cat, f)
        if already_existing == False:
            self.res_cat.append(json_body)
            print(json_body)
            with open(self.res_cat, "w") as f:
                json.dump(self.res_cat, f)
            return "Resource catalog not found. New resource catalog inserted with success"
        else:
            return "Resource catalog modified with success"
    else:
        error_string = "incorrect URI or PARAMETERS" + {len(uri)}
        raise cherrypy.HTTPError(400, error_string)