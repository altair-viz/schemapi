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

    simple_types = ["boolean", "null", "number", "string"]
    valid_types = simple_types + ["array", "object"]
    traitlet_map = {'array': {'cls': 'T.List'},
                    'boolean': {'cls': 'jst.JSONBoolean'},
                    'null': {'cls': 'jst.JSONNull'},
                    'number': {'cls': 'jst.JSONNumber'},
                    'string': {'cls': 'jst.JSONString'},
                   }

    def __init__(self, schema, context=None, parent=None, name=None):
        self.schema = schema
        self.parent = parent
        self.name = name

        # if context is not given, then assume this is a root instance that
        # defines its context
        self.context = context or schema

    @classmethod
    def _get_trait_code(cls, typecode):
        """Create the trait code for the given typecode"""
        if typecode in cls.simple_types:
            info = cls.traitlet_map[typecode]
            return construct_function_call(info['cls'],
                                           *info.get('args', []),
                                           **info.get('kwargs', {}))
        elif typecode == 'array':
            raise NotImplementedError('trait code for type = "array"')
        elif typecode == 'object':
            raise NotImplementedError('trait code for type = "object"')
        elif isinstance(typecode, list):
            # TODO: if Null is in the list, then add keyword allow_none=True
            arg = "[{0}]".format(', '.join(cls._get_trait_code(typ)
                                           for typ in typecode))
            return construct_function_call('T.Union', Variable(arg))
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
    def trait_code(self):
        return self._get_trait_code(self.type)

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

    def object_code(self):
        return jinja2.Template(self.object_template).render(cls=self)

    def submodule_spec(self):
        return {
            'code': jinja2.Template(self.object_template).render(cls=self),
            'dependencies': ['jstraitlets']
        }

    def module_spec(self, packagename='_schema'):
        assert self.is_root

        submodroot = self.classname.lower()

        init_spec = {
            'code': ('from .jstraitlets import *\n'
                     f'from .{submodroot} import *\n'),
            'dependencies': ['jstraitlets', submodroot]
        }

        jstraitlets_spec = {
            'code': open(os.path.join(os.path.dirname(__file__),
                                      'json_traitlets.py')).read()
        }

        modspec = {
            'package': packagename,
            'contents': {
                '__init__.py': init_spec,
                'jstraitlets.py': jstraitlets_spec,
                f'{submodroot}.py': self.submodule_spec()
            }
        }
        return modspec
