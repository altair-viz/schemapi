import jinja2

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
    draft = 4

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

    @property
    def type(self):
        # TODO: should the default type be considered object?
        return self.schema.get('type', 'object')

    @property
    def trait_code(self):
        return SchemaType(self.type).get_trait_code()

    @property
    def classname(self):
        if self.name:
            return self.name
        elif self.context is self.schema:
            return "RootInstance"
        else:
            raise NotImplementedError("Anonymous class name")

    @property
    def baseclass(self):
        return "T.HasTraits"

    @property
    def imports(self):
        return ["import traitlets as T"]

    @property
    def properties(self):
        """Return property dictionary wrapped as JSONSchema objects"""
        properties = self.schema.get('properties', {})
        return {key: self.make_child(val)
                for key, val in properties.items()}

    def object_code(self):
        return jinja2.Template(self.object_template).render(cls=self)


class SchemaType(object):
    """Tools for interpreting schema types"""
    simple_types = ["boolean", "null", "number", "string"]
    valid_types = simple_types + ["array", "object"]
    traitlet_map = {'array': {'cls': 'T.List'},
                    'boolean': {'cls': 'T.Bool'},
                    'null': {'cls': 'T.Integer',
                             'kwargs': {'allow_none': True,
                                        'minimum': 1,
                                        'maximum': 0}},
                    'number': {'cls': 'T.Float'},
                    'string': {'cls': 'T.Unicode'},
                   }

    def __init__(self, typecode):
        self.typecode = typecode

    def get_trait_code(self):
        if self.typecode in self.simple_types:
            info = self.traitlet_map[self.typecode]
            return construct_function_call(info['cls'],
                                           *info.get('args', []),
                                           **info.get('kwargs', {}))
        elif self.typecode == 'array':
            raise NotImplementedError('type = "array"')
        elif self.typecode == 'object':
            raise NotImplementedError('trait code for type = "object"')
        elif isinstance(self.typecode, list):
            # TODO: if Null is in the list, then add keyword allow_none=True
            arg = "[{0}]".format(','.join(SchemaType(typ).get_trait_code()
                                          for typ in self.typecode))
            return construct_function_call('T.Union', Variable(arg))
        else:
            raise ValueError(f"unrecognized type identifier: {typecode}")
