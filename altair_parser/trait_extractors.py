"""Extractors for trait codes"""
import jinja2

from .utils import construct_function_call, Variable


OBJECT_TEMPLATE = '''
class {{ cls.classname }}({{ cls.baseclass }}):
    """{{ cls.classname }} class

    Attributes
    ----------
    {%- for (name, prop) in cls.wrapped_properties().items() %}
    {{ name }} : {{ prop.type }}
        {{ prop.description }}
    {%- endfor %}
    """
    _additional_traits = {{ cls.default_trait }}
    {%- for (name, prop) in cls.wrapped_properties().items() %}
    {{ name }} = {{ prop.trait_code }}
    {%- endfor %}
'''

REFUNION_TEMPLATE = '''
class {{ cls.classname }}(jst.HasTraitsUnion):
    _classes = ({% for name in options %}"{{ name }}", {%- endfor %})
'''


class ImportStatement(object):
    def __init__(self, path, names):
        self.path = path
        self.names = names

    def __repr__(self):
        return "from {0} import {1}".format(self.path, ', '.join(self.names))


class TraitCodeExtractor(object):
    """Base class for trait code extractors.

    An ordered list of these is passed to JSONSchema, and they are used to
    extract appropriate trait codes and object codes reflecting the schema.

    Methods to Override
    -------------------
    check :
        return True if this class can handle self.schema
    object_code :
        return the string of python code to define this object.
    trait_code :
        return the string of python code to reference this object as a trait.
    object_imports :
        return a list of import statements required for defining the object
    trait_imports :
        return a list of import statements required for defining the trait
    """
    def __init__(self, schema, typecode=None):
        self.schema = schema
        self.typecode = typecode or schema.type

    def check(self):
        raise NotImplementedError()

    def trait_code(self, **kwargs):
        raise NotImplementedError()

    def object_code(self, **kwargs):
        return ""

    def trait_imports(self):
        raise NotImplementedError()

    def object_imports(self):
        raise NotImplementedError()


###############################################################################
# Extractor classes, in the order of checks

class HasTraitsUnionTraitCode(TraitCodeExtractor):
    def check(self):
        if (self.schema.is_root or self.schema.name) and 'anyOf' in self.schema:
            return all(self.schema.make_child(schema).is_reference
                       for schema in self.schema['anyOf'])
        else:
            return False

    def trait_code(self, **kwargs):
        return construct_function_call('jst.JSONInstance',
                                       self.schema.full_classname,
                                       **kwargs)

    def object_code(self):
        template = jinja2.Template(REFUNION_TEMPLATE)
        return template.render(cls=self.schema,
                               options=[self.schema.make_child(ref).full_classname
                                        for ref in self.schema['anyOf']])


class RefTraitCode(TraitCodeExtractor):
    def check(self):
        return '$ref' in self.schema

    def trait_code(self, **kwargs):
        ref = self.schema.wrapped_ref()
        if ref.really_is_trait():
            ref.metadata = self.schema.metadata
            return ref.trait_code
        else:
            return construct_function_call('jst.JSONInstance',
                                           ref.full_classname,
                                           **kwargs)

    def object_code(self):
        ref = self.schema.wrapped_ref()
        if ref.really_is_trait():
            return ""
        else:
            template = jinja2.Template(REFUNION_TEMPLATE)
            return template.render(cls=self.schema,
                                   options=[self.schema.wrapped_ref().full_classname])

    def trait_imports(self):
        ref = self.schema.wrapped_ref()
        if ref.is_trait:
            return ref.trait_imports
        else:
            return [f'from .{ref.modulename} import {ref.classname}']


class NotTraitCode(TraitCodeExtractor):
    def check(self):
        return 'not' in self.schema

    def trait_code(self, **kwargs):
        not_this = self.schema.make_child(self.schema['not']).trait_code
        return construct_function_call('jst.JSONNot', Variable(not_this),
                                       **kwargs)

    def trait_imports(self):
        return self.schema.make_child(self.schema['not']).trait_imports


class AnyOfTraitCode(TraitCodeExtractor):
    def check(self):
        return 'anyOf' in self.schema

    def trait_code(self, **kwargs):
        children = [Variable(self.schema.make_child(sub_schema).trait_code)
                    for sub_schema in self.schema['anyOf']]
        return construct_function_call('jst.JSONAnyOf', Variable(children),
                                       **kwargs)

    def trait_imports(self):
        return sum((self.schema.make_child(sub_schema).trait_imports
                    for sub_schema in self.schema['anyOf']), [])


class AllOfTraitCode(TraitCodeExtractor):
    def check(self):
        return 'allOf' in self.schema

    def trait_code(self, **kwargs):
        children = [Variable(self.schema.make_child(sub_schema).trait_code)
                    for sub_schema in self.schema['allOf']]
        return construct_function_call('jst.JSONAllOf', Variable(children),
                                       **kwargs)

    def trait_imports(self):
        return sum((self.schema.make_child(sub_schema).trait_imports
                    for sub_schema in self.schema['allOf']), [])


class OneOfTraitCode(TraitCodeExtractor):
    def check(self):
        return 'oneOf' in self.schema

    def trait_code(self, **kwargs):
        children = [Variable(self.schema.make_child(sub_schema).trait_code)
                    for sub_schema in self.schema['oneOf']]
        return construct_function_call('jst.JSONOneOf', Variable(children),
                                       **kwargs)

    def trait_imports(self):
        return sum((self.schema.make_child(sub_schema).trait_imports
                    for sub_schema in self.schema['oneOf']), [])


class EnumTraitCode(TraitCodeExtractor):
    def check(self):
        return 'enum' in self.schema

    def trait_code(self, **kwargs):
        return construct_function_call('jst.JSONEnum',
                                       self.schema["enum"],
                                       **kwargs)


class SimpleTraitCode(TraitCodeExtractor):
    simple_types = ["boolean", "null", "number", "integer", "string"]
    classes = {'boolean': 'jst.JSONBoolean',
               'null': 'jst.JSONNull',
               'number': 'jst.JSONNumber',
               'integer': 'jst.JSONInteger',
               'string': 'jst.JSONString'}
    validation_keys = {'number': ['minimum', 'exclusiveMinimum',
                                  'maximum', 'exclusiveMaximum',
                                  'multipleOf'],
                       'integer': ['minimum', 'exclusiveMinimum',
                                   'maximum', 'exclusiveMaximum',
                                   'multipleOf']}

    def check(self):
        return self.typecode in self.simple_types

    def trait_code(self, **kwargs):
        cls = self.classes[self.typecode]
        keys = self.validation_keys.get(self.typecode, [])
        kwargs.update({key: self.schema[key] for key in keys
                       if key in self.schema})
        return construct_function_call(cls, **kwargs)


class ArrayTraitCode(TraitCodeExtractor):
    def check(self):
        return self.schema.type == 'array'

    def trait_code(self, **kwargs):
        # TODO: implement items as list and additionalItems
        items = self.schema['items']
        if 'minItems' in self.schema:
            kwargs['minlen'] = self.schema['minItems']
        if 'maxItems' in self.schema:
            kwargs['maxlen'] = self.schema['maxItems']
        if 'uniqueItems' in self.schema:
            kwargs['uniqueItems'] = self.schema['uniqueItems']
        if isinstance(items, list):
            raise NotImplementedError("'items' keyword as list")
        else:
            itemtype = self.schema.make_child(items).trait_code
        return construct_function_call('jst.JSONArray', Variable(itemtype),
                                       **kwargs)

    def trait_imports(self):
        items = self.schema['items']
        if isinstance(items, list):
            raise NotImplementedError("'items' keyword as list")
        else:
            return self.schema.make_child(items).trait_imports


class CompoundTraitCode(TraitCodeExtractor):
    simple_types = SimpleTraitCode.simple_types

    def check(self):
        return (isinstance(self.typecode, list) and
                all(typ in self.simple_types for typ in self.typecode))

    def trait_code(self, **kwargs):
        if 'null' in self.typecode:
            kwargs['allow_none'] = True
        typecode = [typ for typ in self.typecode if typ != 'null']

        if len(typecode) == 1:
            return SimpleTraitCode(self.schema,
                                   typecode[0]).trait_code(**kwargs)
        else:
            item_kwargs = {key: val for key, val in kwargs.items()
                           if key not in ['allow_none', 'allow_undefined']}
            arg = "[{0}]".format(', '.join(SimpleTraitCode(self.schema, typ).trait_code(**item_kwargs)
                                           for typ in typecode))
            return construct_function_call('jst.JSONUnion', Variable(arg),
                                           **kwargs)


class ObjectTraitCode(TraitCodeExtractor):
    def check(self):
        return self.typecode == 'object'

    def trait_code(self, **kwargs):
        trait_codes = {name: Variable(prop.trait_code) for (name, prop)
                       in self.schema.wrapped_properties().items()}
        defn = construct_function_call("T.MetaHasTraits", 'Mapping',
                                       (Variable(self.schema.baseclass),),
                                       trait_codes)
        return construct_function_call('jst.JSONInstance', Variable(defn),
                                       **kwargs)

    def object_code(self, **kwargs):
        template = jinja2.Template(OBJECT_TEMPLATE)
        return template.render(cls=self.schema)
