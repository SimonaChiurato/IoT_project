# service catalog
import json


class HomeCatalog:
    def __init__(self):
        self.settings = "HomeCatalog_settings.json"
        self.cat = json.load(open(self.settings))
        with open(self.settings, "w") as myfile:
            myfile.write(json.dumps(self.cat))

    def returnAllPatients(self):
        result = {'names': []}
        for res in self.cat["resource_catalogs"]["patients"]:
            result['names'].append(res['patient'])
        return result

    def searchPatient(self, params):
        found = 0
        for entry in self.cat["resource_catalogs"]["patients"]:
            if (entry["patient"] == params["patient"]):
                found = 1
                result = self.cat["resource_catalogs"].copy()
                result.pop("patients")
                result["patient"] = entry["patient"]
                result["base_topic"] = entry["base_topic"]
                return result
        return found

    def updateResCat(self, message):
        j = 0
        if self.cat["resource_catalogs"] != {}:
            for entry in self.cat["resource_catalogs"]:
                if entry != "patients" and self.cat["resource_catalogs"][entry] != message[entry]:
                    self.cat["resource_catalogs"][entry] = message[entry]
                j += 1
            i = 0
            for entry in self.cat["resource_catalogs"]["patients"]:
                if entry["base_topic"] == message["patients"][i]["base_topic"]:
                    already_existing = True
                    entry["patient"] = message["patients"][i]["patient"]
                    i += 1
                    print("Resource catalog already existing")

        else:
            self.cat["resource_catalogs"] = message
            with open(self.settings, "w") as f:
                json.dump(self.cat, f, indent=4)
            print("Resource catalog inserted with success")
        return self.cat
