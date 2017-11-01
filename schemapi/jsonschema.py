import warnings
import json

from . import utils
from .traitlets import JSONSchemaTraitlets


class JSONSchema(object):
    def __init__(self, schema, root_name='Root',
                 definition_tags=('definitions',),
                 root=None, name=None):
        if not isinstance(schema, dict):
            raise ValueError("schema should be supplied as a dict")

        self.schema = schema
        self.name = name
        self.root_name = root_name

        # if root is not given, then assume this is a root instance
        self.root = root or self
        self._definition_tags = definition_tags
        self._trait_extractor = None

    @property
    def definitions(self):
        """dictionary of definition name to raw schemas they point to"""
        definitions = {}#self.root_name: self.schema}
        for tag in self._definition_tags:
            definitions.update(self.schema.get(tag, {}))
        return definitions

    @classmethod
    def from_json_file(cls, filename, **kwargs):
        """Instantiate a JSONSchema object from a JSON file"""
        import json
        with open(filename) as f:
            schema = json.load(f)
        return cls(schema, **kwargs)

    def initialize_child(self, schema, name=None):
        """
        Make a child instance, appropriately defining the root
        """
        return self.__class__(schema, root=self.root, name=name)

    @property
    def traitlets(self):
        return JSONSchemaTraitlets(self)

    def load_module(self, *args, **kwargs):
        warnings.warn(('schema.load_module() is deprecated. '
                       'Use schema.traitlets.load_module()'),
                       DeprecationWarning)
        return self.traitlets.load_module(*args, **kwargs)

    def write_module(self, *args, **kwargs):
        warnings.warn(('schema.write_module() is deprecated. '
                       'Use schema.traitlets.write_module()'),
                       DeprecationWarning)
        return self.traitlets.write_module(*args, **kwargs)

    def source_tree(self, *args, **kwargs):
        warnings.warn(('schema.source_tree() is deprecated. '
                       'Use schema.traitlets.source_tree()'),
                       DeprecationWarning)
        return self.traitlets.source_tree(*args, **kwargs)
