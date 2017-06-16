import jinja2
import os

from .utils import construct_function_call, Variable


OBJECT_TEMPLATE = """
{%- for import in cls.imports %}
{{ import }}
{%- endfor %}

class {{ cls.classname }}({{ cls.baseclass }}):
    {%- for (name, prop) in cls.properties.items() %}
    {{ name }} = {{ prop.trait_code }}
    {%- endfor %}
"""

class JSONSchema(object):
    """A class to wrap JSON Schema objects and reason about their contents"""
    object_template = OBJECT_TEMPLATE
    __draft__ = 4

    simple_types = ["boolean", "null", "number", "integer", "string"]
    valid_types = simple_types + ["array", "object"]
    traitlet_map = {'array': {'cls': 'jst.JSONArray'},
                    'boolean': {'cls': 'jst.JSONBoolean'},
                    'null': {'cls': 'jst.JSONNull'},
                    'number': {'cls': 'jst.JSONNumber'},
                    'integer': {'cls': 'jst.JSONInteger'},
                    'string': {'cls': 'jst.JSONString'},
                   }

    def __init__(self, schema, context=None, parent=None, name=None):
        self.schema = schema
        self.parent = parent
        self.name = name

        # if context is not given, then assume this is a root instance that
        # defines its context
        self.context = context or schema

    @property
    def trait_code(self):
        """Create the trait code for the given typecode"""
        typecode = self.type

        if typecode in self.simple_types:
            info = self.traitlet_map[typecode]
            return construct_function_call(info['cls'],
                                           *info.get('args', []),
                                           **info.get('kwargs', {}))
        elif typecode == 'array':
            itemtype = self.make_child(schema['items']).trait_code
            return 'jst.JSONArray({0})'.format(itemtype)
        elif typecode == 'object':
            raise NotImplementedError('trait code for type = "object"')
        elif isinstance(typecode, list):
            # TODO: if Null is in the list, then add keyword allow_none=True
            arg = "[{0}]".format(', '.join(self.make_child({'type':typ}).trait_code
                                           for typ in typecode))
            return construct_function_call('jst.JSONUnion', Variable(arg))
        else:
            raise ValueError(f"unrecognized type identifier: {typecode}")

    def make_child(self, schema, name=None):
        """
        Make a child instance, appropriately defining the parent and context
        """
        return self.__class__(schema, context=self.context,
                              parent=self, name=name)

    @property
    def type(self):
        # TODO: should the default type be considered object?
        return self.schema.get('type', 'object')

    @property
    def is_root(self):
        return self.context is self.schema

    @property
    def classname(self):
        if self.name:
            return self.name
        elif self.is_root:
            return "RootInstance"
        else:
            raise NotImplementedError("Anonymous class name")

    @property
    def baseclass(self):
        return "T.HasTraits"

    @property
    def imports(self):
        return ["import traitlets as T",
                "from . import jstraitlets as jst"]

    @property
    def properties(self):
        """Return property dictionary wrapped as JSONSchema objects"""
        properties = self.schema.get('properties', {})
        return {key: self.make_child(val)
                for key, val in properties.items()}

    def module_spec(self):
        assert self.is_root
        submodroot = self.classname.lower()

        modspec = {
            '__init__.py': ('from .jstraitlets import *\n'
                            f'from .{submodroot} import *\n'),
            'jstraitlets.py': open(os.path.join(os.path.dirname(__file__),
                                   'json_traitlets.py')).read(),
            f'{submodroot}.py': jinja2.Template(self.object_template).render(cls=self)
        }
        return modspec
