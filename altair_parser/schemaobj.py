import json


class VLSchema(object):
    """Wrapper for a Vega/Vega-Lite JSON Schema"""

    def __init__(self, schema):
        self.schema = schema

    @property
    def definitions(self):
        return self.schema['definitions']

    @classmethod
    def from_file(cls, file_or_filename):
        if hasattr(file_or_filename, 'read'):
            return cls(json.load(file_or_filename))
        else:
            with open(filename) as f:
                return cls(json.load(f))

    @classmethod
    def from_string(cls, json_string):
        return cls(json.loads(json_string))
    
