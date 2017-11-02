import warnings
import json

from . import utils
from .traitlets import JSONSchemaTraitlets
from .validators import ValidatorList


class JSONSchema(object):
    """Wrapper for a JSON schema

    Parameters
    ----------
    schema : dict
        a jsonschema dictionary

    Attributes
    ----------
    schema : dict
        the schema dictionary
    root : JSONSchema object
        a pointer to the root schema
    validators : list
        a list of Validator classes for this level of the schema
    parents : set
        a list of parent objects to the current schema

    Notes
    -----
    The root JSONSchema has a _registry attribute, which is a dictionary mapping
    unique hashes of each schema to a JSONSchema object which wraps it. When the
    tree of schema objects is created, this registry is used to identify
    when two schemas are identical, both for efficiency and to properly handle
    cyclical schema definitions.

    Because of this, the ``parents`` attribute is able to point to all parents
    of each unique schema, even if the spec occurs multiple times in the schema
    tree.

    Additionally, each schema will match zero or more "validator" classes, which
    can be used to validate input with the validate() method.
    """
    def __init__(self, schema, warn_on_unused=True,
                 root_name='Root',
                 name=None, **kwds):
        unrecognized_args = kwds.keys() - {'root'}
        if unrecognized_args:
            raise ValueError('Unrecognized arguments to JSONSchema: {0}'
                             ''.format(unrecognized_args))
        self.schema = schema
        self.root = kwds.get('root', self)
        self.validators = ValidatorList(self)
        self.parents = set()

        # remove these?
        self.warn_on_unused = warn_on_unused
        self._name = name
        self.root_name = root_name

        # Because of the use of the registry, we need to finish object creation
        # before instantiating children. For that reason, we recursively
        # create children from the root instance.
        if self is self.root:
            hsh = self._schema_hash()
            self._registry = {hsh: self}
            self._schema_to_name = {hsh: '#'}
            self._definitions = {'#': self.schema}
            self._recursively_create_children()

    def _schema_hash(self):
        return utils.hash_schema(self.schema)

    @classmethod
    def from_file(cls, file):
        try:
            schema = json.load(file)
        except AttributeError:
            with open(file, 'r') as f:
                schema = json.load(f)
        return cls(schema)

    @property
    def registry(self):
        """Registry of instantiated JSONSchema objects in this tree"""
        return self.root._registry

    @property
    def ref(self):
        return self.root._schema_to_name.get(self._schema_hash(), None)

    @property
    def name(self):
        """Return the object name if present, otherwise return None"""
        if self is self.root and self.root_name:
            return self.root_name
        elif self._name:
            return self._name
        elif self.ref:
            return self.ref.split('/')[-1]
        else:
            return None

    def _recursively_create_children(self, seen=None):
        """
        Recursively create all children schemas,
        ignoring any hashes that appear in seen set.
        """
        seen = seen or set()
        for child in self.children:
            hsh = child._schema_hash()
            if hsh not in seen:
                seen.add(hsh)
                child._recursively_create_children(seen)

    def initialize_child(self, schema, name=None):
        """Return a JSONSchema object wrapping a child schema"""
        key = utils.hash_schema(schema)
        if key not in self.registry:
            self.registry[key] = JSONSchema(schema, root=self.root, name=name)
        obj = self.registry[key]
        if self not in obj.parents:
            obj.parents.add(self)
        return obj

    def resolve_ref(self, ref):
        """Resolve a reference within a schema"""
        if ref not in self.root._definitions:
            keys = ref.split('/')
            if keys[0] != '#':
                raise ValueError("$ref = {0} not recognized: must start with #"
                                 "".format(self.schema['$ref']))
            refschema = self.root.schema
            for key in keys[1:]:
                refschema = refschema[key]
            self.root._definitions[ref] = refschema
            self.root._schema_to_name[utils.hash_schema(refschema)] = ref
        return self.root._definitions[ref]

    @property
    def children(self):
        return [self.initialize_child(schema)
                for schema in self.iter_child_schemas()]

    def iter_child_schemas(self):
        for key in ['properties', 'patternProperties']:
            for child in self.schema.get(key, {}).values():
                yield child
        for key in ['anyOf', 'oneOf', 'allOf']:
            for child in self.schema.get(key, []):
                yield child
        for key in ['additionalProperties', 'not', 'items']:
            val = self.schema.get(key, None)
            if isinstance(val, dict):
                yield val
        if '$ref' in self.schema:
            yield self.resolve_ref(self.schema['$ref'])

    @property
    def definitions(self):
        """dictionary of definition name to raw schemas they point to"""
        def get_name(defname):
            if defname == '#':
                return self.root_name
            else:
                return defname.split('/')[-1]
        return {get_name(name): schema
                for name, schema in self._definitions.items()}

    def validate(self, obj):
        self.validators.validate(obj)

    def __repr__(self):
        return "JSONSchema({0})".format(self.validators)

    def __eq__(self, other):
        return self.schema == other.schema

    def __hash__(self):
        return hash(self._schema_hash())

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
