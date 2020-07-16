import json
from munch import Munch

class Tablemap:
    def __init__(self, path):
        aux = json.loads(open(path).read())
        self.tablemap_areas = []
        for json_ in aux:
            self.tablemap_areas.append(Munch(json_))
