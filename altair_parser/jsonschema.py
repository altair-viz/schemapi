import jinja2
import os

from .utils import construct_function_call, Variable


OBJECT_TEMPLATE = """
{%- for import in cls.imports %}
{{ import }}
{%- endfor %}

class {{ cls.classname }}({{ cls.baseclass }}):
    {%- for (name, prop) in cls.wrapped_properties().items() %}
    {{ name }} = {{ prop.trait_code }}
    {%- endfor %}
"""

class JSONSchema(object):
    """A class to wrap JSON Schema objects and reason about their contents"""
    object_template = OBJECT_TEMPLATE
    __draft__ = 4

    _cached_references = {}
    simple_types = ["boolean", "null", "number", "integer", "string"]
    valid_types = simple_types + ["array", "object"]
    traitlet_map = {'array': {'cls': 'jst.JSONArray'},
                    'boolean': {'cls': 'jst.JSONBoolean'},
                    'null': {'cls': 'jst.JSONNull'},
                    'number': {'cls': 'jst.JSONNumber'},
                    'integer': {'cls': 'jst.JSONInteger'},
                    'string': {'cls': 'jst.JSONString'},
                   }
    attr_defaults = {'title': '',
                     'description': '',
                     'properties': {},
                     'definitions': {},
                     'default': None,
                     'examples': {},
                     'type': 'object'}

    def __init__(self, schema, context=None, parent=None, name=None):
        self.schema = schema
        self.parent = parent
        self.name = name

        # if context is not given, then assume this is a root instance that
        # defines its context
        self.context = context or schema

    def make_child(self, schema, name=None):
        """
        Make a child instance, appropriately defining the parent and context
        """
        return self.__class__(schema, context=self.context,
                              parent=self, name=name)

    def __getattr__(self, attr):
        if attr in self.attr_defaults:
            return self.schema.get(attr, self.attr_defaults[attr])
        raise AttributeError(f"'{self.__class__.__name__}' object "
                             f"has no attribute '{attr}'")

    @property
    def is_root(self):
        return self.context is self.schema

    @property
    def is_trait(self):
        return self.type != 'object'

    @property
    def is_object(self):
        return self.type == 'object'

    @property
    def classname(self):
        if self.name:
            return self.name
        elif self.is_root:
            return "RootInstance"
        else:
            raise NotImplementedError("Anonymous class name")

    @property
    def filename(self):
        return self.classname.lower() + '.py'

    @property
    def baseclass(self):
        return "T.HasTraits"

    @property
    def imports(self):
        # TODO: add imports to properties
        return ["import traitlets as T",
                "from . import jstraitlets as jst"]

    def wrapped_definitions(self):
        return {name.lower(): self.make_child(schema, name=name)
                for name, schema in self.definitions.items()}

    def wrapped_properties(self):
        """Return property dictionary wrapped as JSONSchema objects"""
        return {key: self.make_child(val)
                for key, val in self.properties.items()}

    @property
    def trait_code(self):
        """Create the trait code for the given typecode"""
        typecode = self.type

        # TODO: check how jsonschema handles multiple entries...
        #       e.g. anyOf + enum or $ref + oneOf

        if "not" in self.schema:
            raise NotImplementedError("'not' keyword")
        elif "$ref" in self.schema:
            raise NotImplementedError("'$ref' keyword")
        elif "anyOf" in self.schema:
            raise NotImplementedError("'anyOf' keyword")
        elif "allOf" in self.schema:
            raise NotImplementedError("'allOf' keyword")
        elif "oneOf" in self.schema:
            raise NotImplementedError("'oneOf' keyword")
        elif "enum" in self.schema:
            return construct_function_call('jst.JSONEnum', self.schema["enum"])
        elif typecode in self.simple_types:
            # TODO: implement checks like maximum, minimum, format, etc.
            info = self.traitlet_map[typecode]
            return construct_function_call(info['cls'],
                                           *info.get('args', []),
                                           **info.get('kwargs', {}))
        elif typecode == 'array':
            # TODO: implement checks like maxLength, minLength, etc.
            items = self.schema['items']
            if isinstance(items, list):
                # TODO: need to implement this in the JSONArray traitlet
                # Also need to check value of "additionalItems"
                raise NotImplementedError("'items' keyword as list")
            else:
                itemtype = self.make_child(items).trait_code
            return construct_function_call('jst.JSONArray', Variable(itemtype))
        elif typecode == 'object':
            raise NotImplementedError('trait code for type = "object"')
        elif isinstance(typecode, list):
            # TODO: if Null is in the list, then add keyword allow_none=True
            arg = "[{0}]".format(', '.join(self.make_child({'type':typ}).trait_code
                                           for typ in typecode))
            return construct_function_call('jst.JSONUnion', Variable(arg))
        else:
            raise ValueError(f"unrecognized type identifier: {typecode}")

    def object_code(self):
        return jinja2.Template(self.object_template).render(cls=self)

    def module_spec(self):
        assert self.is_root
        submodroot = self.classname.lower()

        modspec = {
            'jstraitlets.py': open(os.path.join(os.path.dirname(__file__),
                                   'json_traitlets.py')).read(),
            self.filename: self.object_code()
        }


        modspec['__init__.py'] = ('from .jstraitlets import *\n'
                                  f'from .{submodroot} import *\n')

        modspec.update({schema.filename: schema.object_code()
                        for schema in self.wrapped_definitions().values()})

        return modspec

    def get_reference(self, ref, cache=True):
        """
        Get the JSONSchema object for the
        """
        if cache and ref in self._cached_references:
            return self._cached_references[ref]

        path = ref.split('/')
        if path[0] != '#':
            raise ValueError(f"Unrecognized $ref format: '{ref}'")
        try:
            schema = self.context
            for key in path[1:]:
                schema = schema[key]
        except KeyError:
            raise ValueError(f"$ref='{ref}' not present in the schema")

        wrapped_schema = self.make_child(schema)
        if cache:
            self._cached_references[ref] = wrapped_schema
        return wrapped_schema
