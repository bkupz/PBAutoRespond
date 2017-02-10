# Brandon Kupczyk

import json
from collections import namedtuple


class json_decoder(): #Decodes json obejcts into accessable objects in python
    """
    This Class is used to decode the JSON objects sent from the Pushbullet service.
    """
    @classmethod
    def decode(cls,data):
        rturn = cls.json2obj(data)
        return rturn

    @classmethod
    def _json_object_hook(cls, d): return namedtuple('X', d.keys())(*d.values())

    @classmethod
    def json2obj(cls, data): return json.loads(data, object_hook=cls._json_object_hook)
