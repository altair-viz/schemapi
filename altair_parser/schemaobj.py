import json
import warnings


class JSONWrapperBase(object):
    """Base class for JSON wrappers"""
    required_entries = []

    def __init__(self, schema, name=''):
        self.schema = schema
        self.name = name

        for entry in self.required_entries:
            if entry not in schema:
                warnings.warn(f'{self.__class__.__name__} "{name}" does not contain a "{entry}" entry')

    @classmethod
    def from_dict(cls, dct):
        return cls(dct)

    @classmethod
    def from_file(cls, file_or_filename):
        if hasattr(file_or_filename, 'read'):
            return cls(json.load(file_or_filename))
        else:
            with open(file_or_filename) as f:
                return cls(json.load(f), name=file_or_filename)

    @classmethod
    def from_string(cls, json_string):
        return cls(json.loads(json_string))


class VegaSchema(JSONWrapperBase):
    """Wrapper for a Vega/Vega-Lite JSON Schema"""
    required_entries = ["$schema", "$ref", "definitions"]

    @property
    def definitions(self):
        return {name: VegaSchemaDefinition(value, name=name)
                for name, value in self.schema['definitions'].items()}


class VegaSchemaDefinition(JSONWrapperBase):
    """Wrapper for a Definition within a Vega(-Lite) Schema"""

    @property
    def properties(self):
        props = self.schema.get('properties', {})
        return {name: VegaProperty(prop, name=name)
                for name, prop in props.items()}

    def __repr__(self):
        keys = set(self.schema.keys())
        return f"VegaSchemaDefinition(properties={keys})"


class VegaProperty(JSONWrapperBase):
    """Wrapper for a Vega(-Lite) definition property"""

    def __repr__(self):
        return f"VegaProperty({self.schema})"

    @property
    def type(self):
        return self.schema.get('type', None)

    @property
    def description(self):
        return self.schema.get('description', None)
