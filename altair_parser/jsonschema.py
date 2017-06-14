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

    def __init__(self, schema, context=None, parent=None, name=None):
        self.schema = schema
        self.context = context or schema
        self.parent = parent
        self.name = name

    def make_child(self, schema, name=None):
        return self.__class__(schema, context=self.context, parent=self, name=name)

    @property
    def type(self):
        # TODO: should the default type be considered object?
        return self.schema.get('type', 'object')

    @property
    def trait_code(self):
        type_dict = {'string': 'T.Unicode()',
                     'number': 'T.Float()',
                     'integer': 'T.Integer()',
                     'boolean': 'T.Bool()'}
        if self.type not in type_dict:
            raise NotImplementedError()
        return type_dict[self.type]

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
