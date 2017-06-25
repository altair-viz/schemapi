"""Extractors for trait codes"""
from .utils import construct_function_call, Variable


class ImportStatement(object):
    def __init__(self, path, names):
        self.path = path
        self.names = names

    def __repr__(self):
        return "from {0} import {1}".format(self.path, ', '.join(self.names))


class TraitCodeExtractor(object):
    """Base class for trait code extractors.

    An ordered list of these is passed to JSONSchema, and they are used to
    extract appropriate trait codes.
    """
    def __init__(self, schema, typecode=None):
        self.schema = schema
        self.typecode = typecode or schema.type

    def check(self):
        raise NotImplementedError()

    def trait_code(self, **kwargs):
        raise NotImplementedError()

    def imports(self):
        return []


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


class RefTraitCode(TraitCodeExtractor):
    def check(self):
        return '$ref' in self.schema

    def trait_code(self, **kwargs):
        ref = self.schema.wrapped_ref()
        if ref.is_object:
            return construct_function_call('jst.JSONInstance',
                                           ref.full_classname,
                                           **kwargs)
        else:
            ref = ref.copy()  # TODO: maybe can remove this?
            ref.metadata = self.schema.metadata
            return ref.trait_code

    def imports(self):
        ref = self.schema.wrapped_ref()
        if ref.is_object:
            return [f'from .{ref.modulename} import {ref.classname}']
        else:
            return ref.trait_imports


class EnumTraitCode(TraitCodeExtractor):
    def check(self):
        return 'enum' in self.schema

    def trait_code(self, **kwargs):
        return construct_function_call('jst.JSONEnum',
                                       self.schema["enum"],
                                       **kwargs)


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

    def imports(self):
        items = self.schema['items']
        if isinstance(items, list):
            raise NotImplementedError("'items' keyword as list")
        else:
            return self.schema.make_child(items).trait_imports


class AnyOfTraitCode(TraitCodeExtractor):
    def check(self):
        return 'anyOf' in self.schema

    def trait_code(self, **kwargs):
        children = [Variable(self.schema.make_child(sub_schema).trait_code)
                    for sub_schema in self.schema['anyOf']]
        return construct_function_call('jst.JSONAnyOf', Variable(children),
                                       **kwargs)

    def imports(self):
        return sum((self.schema.make_child(sub_schema).trait_imports
                    for sub_schema in self.schema['anyOf']), [])


class OneOfTraitCode(TraitCodeExtractor):
    def check(self):
        return 'oneOf' in self.schema

    def trait_code(self, **kwargs):
        children = [Variable(self.schema.make_child(sub_schema).trait_code)
                    for sub_schema in self.schema['oneOf']]
        return construct_function_call('jst.JSONOneOf', Variable(children),
                                       **kwargs)

    def imports(self):
        return sum((self.schema.make_child(sub_schema).trait_imports
                    for sub_schema in self.schema['oneOf']), [])


class AllOfTraitCode(TraitCodeExtractor):
    def check(self):
        return 'allOf' in self.schema

    def trait_code(self, **kwargs):
        children = [Variable(self.schema.make_child(sub_schema).trait_code)
                    for sub_schema in self.schema['allOf']]
        return construct_function_call('jst.JSONAllOf', Variable(children),
                                       **kwargs)

    def imports(self):
        return sum((self.schema.make_child(sub_schema).trait_imports
                    for sub_schema in self.schema['allOf']), [])


class NotTraitCode(TraitCodeExtractor):
    def check(self):
        return 'not' in self.schema

    def trait_code(self, **kwargs):
        not_this = self.schema.make_child(self.schema['not']).trait_code
        return construct_function_call('jst.JSONNot', Variable(not_this),
                                       **kwargs)

    def imports(self):
        return self.schema.make_child(self.schema['not']).trait_imports


class ObjectTraitCode(TraitCodeExtractor):
    def check(self):
        return self.typecode == 'object'

    def trait_code(self, **kwargs):
        name = self.schema.as_anonymous_object().full_classname
        return construct_function_call('jst.JSONInstance', name,
                                       **kwargs)
