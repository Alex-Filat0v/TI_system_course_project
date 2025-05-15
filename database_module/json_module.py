import json


class JsonConnector:

    @staticmethod
    def import_to_json(data):
        tmp = {"item": []}

        for item in data["results"]:
            for i in range(len(item["indicators"])):
                tmp["item"].append(item["indicators"][i])

        with open('new.json', 'w') as file:
            json.dump(tmp, file, indent=4)
