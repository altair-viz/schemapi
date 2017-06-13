import warnings
import json


class Schema(object):
    required_keys = set()
    optional_keys = {'description'}

    _constructed_objects = {}

    def __init__(self, schema, name='', context=None):
        self.schema = schema
        self.name = name
        self.context = context
        for key in self.required_keys:
            if key not in self.required_keys:
                raise ValueError(f"key '{key}' required for {self.__class__.__name__}")
        for key in schema:
            if key not in self.required_keys and key not in self.optional_keys:
                warnings.warn(f"key '{key}' not recognized in {self.__class__.__name__}."
                              f"\nFull Schema:\n{schema}\n")

    @classmethod
    def load_file(cls, filename):
        with open(filename) as f:
            schema = json.load(f)
        return cls.new(schema, name='top', context=schema)

    @classmethod
    def infer_subclass(cls, schema):
        keys = [('$schema', RootSchema),
                ('$ref', RefSchema),
                ('allOf', AllOfSchema),
                ('anyOf', AnyOfSchema),
                ('not', NotSchema),
                ('oneOf', OneOfSchema),
                ('enum', EnumSchema)]
        types = {'object': ObjectSchema,
                 'array': ArraySchema,
                 'number': SimpleSchema,
                 'string': SimpleSchema,
                 'boolean': SimpleSchema}
        if len(schema) == 0:
            return EmptySchema

        for key, cls in keys:
            if key in schema:
                return cls

        if 'type' not in schema:
            return UnknownSchema

        typ = schema['type']

        if isinstance(typ, list):
            return CompoundSimpleSchema
        else:
            return types.get(typ, UnknownSchema)

    @classmethod
    def new(cls, schema, name='', context=None):
        if name in cls._constructed_objects:
            return cls._constructed_objects[name]

        schema_class = cls.infer_subclass(schema)
        obj = schema_class(schema, name=name, context=context)
        cls._constructed_objects[name] = obj
        return obj

    def children(self, depth=1):
        yield from []


class EmptySchema(Schema):
    pass


class UnknownSchema(Schema):
    pass


class EnumSchema(Schema):
    required_keys = {'enum', 'type'}


class RefSchema(Schema):
    required_keys = {'$ref'}

    def children(self, depth=1):
        ref = self.schema['$ref']
        path = ref.split('/')
        assert path[0] == '#'
        defn = self.context
        for key in path[1:]:
            defn = defn[key]
        child = Schema.new(defn, name=ref, context=self.context)
        yield child
        if depth > 0:
            yield from child.children(depth - 1)


class RootSchema(RefSchema):
    required_keys = {'$schema', '$ref'}
    optional_keys = {'definitions', 'defs', 'refs', 'description'}


class OneOfSchema(Schema):
    required_keys = {'oneOf'}
    optional_keys = {'description', 'minimum', 'maximum'}

    def children(self, depth=1):
        children = [Schema.new(child, context=self.context)
                    for child in self.schema['oneOf']]
        yield from children
        if depth > 0:
            for child in children:
                yield from child.children(depth - 1)


class AnyOfSchema(Schema):
    required_keys = {'anyOf'}
    optional_keys = {'description', 'minimum', 'maximum'}

    def children(self, depth=1):
        children = [Schema.new(child, context=self.context)
                    for child in self.schema['anyOf']]
        yield from children
        if depth > 0:
            for child in children:
                yield from child.children(depth - 1)


class AllOfSchema(Schema):
    required_keys = {'allOf'}

    def children(self, depth=1):
        children = [Schema.new(child, context=self.context)
                    for child in self.schema['allOf']]
        yield from children
        if depth > 0:
            for child in children:
                yield from child.children(depth - 1)


class NotSchema(Schema):
    required_keys = {'not'}

    def children(self, depth=1):
        child = Schema.new(self.schema['not'], context=self.context)
        yield child
        if depth > 0:
            yield from child.children(depth - 1)


class ObjectSchema(Schema):
    required_keys = {'type', 'properties'}
    optional_keys = {'description', 'additionalProperties', 'required'}

    def children(self, depth=1):
        children = [Schema.new(prop, name=name, context=self.context)
                    for name, prop in self.schema.get('properties', {}).items()]
        yield from children
        if depth > 0:
            for child in children:
                yield from child.children(depth - 1)


class ArraySchema(Schema):
    required_keys = {'type', 'items'}
    optional_keys = {'description', 'minimum', 'maximum'}

    def children(self, depth=1):
        child = Schema.new(self.schema['items'], context=self.context)
        yield child
        if depth > 0:
            yield from child.children(depth - 1)


class SimpleSchema(Schema):
    required_keys = {'type'}
    optional_keys = {'description', 'minimum', 'maximum'}


class CompoundSimpleSchema(Schema):
    required_keys = {'type'}
    optional_keys = {'description', 'minimum', 'maximum'}
