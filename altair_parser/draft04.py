import jinja2


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
        type_dict = {'string': 'T.Unicode()',
                     'number': 'T.Float()',
                     # TODO: remove this hack & create a Null traitlet type.
                     'null': 'T.Integer(allow_none=True, minimum=1, maximum=0)',
                     'boolean': 'T.Bool()'}

        # type can be a list of strings; translate this to a Union
        if isinstance(self.type, list):
            # TODO: if null is in the list, remove it and add "allow_none" to
            # any of the traits.
            if any(typ not in type_dict for typ in self.type):
                raise NotImplementedError(self.type)
            return "T.Union([{0}])".format(','.join(type_dict[typ] for typ in self.type))

        # otherwise type should be a string in type_dict
        if self.type in type_dict:
            return type_dict[self.type]

        # otherwise
        raise ValueError(f"type={self.type} is not a recognized type code")

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
