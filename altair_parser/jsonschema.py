import jinja2
import os
from datetime import datetime

from .utils import construct_function_call, Variable


OBJECT_TEMPLATE = '''# {{ cls.filename }}
# Auto-generated by altair_parser {{ date }}
{%- for import in cls.imports %}
{{ import }}
{%- endfor %}

class {{ cls.classname }}({{ cls.baseclass }}):
    """{{ cls.classname }} class

    Attributes
    ----------
    {%- for (name, prop) in cls.wrapped_properties().items() %}
    {{ name }} : {{ prop.type }}
        {{ prop.description }}
    {%- endfor %}
    """
    {%- for (name, prop) in cls.wrapped_properties().items() %}
    {{ name }} = {{ prop.trait_code }}
    {%- endfor %}
'''


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
                    'number': {'cls': 'jst.JSONNumber',
                               'validation_keys': ['minimum', 'maximum',
                                                   'exclusiveMinimum',
                                                   'exclusiveMaximum',
                                                   'multipleOf']},
                    'integer': {'cls': 'jst.JSONInteger',
                                'validation_keys': ['minimum', 'maximum',
                                                    'exclusiveMinimum',
                                                    'exclusiveMaximum',
                                                    'multipleOf']},
                    'string': {'cls': 'jst.JSONString'},
                   }
    attr_defaults = {'title': '',
                     'description': '',
                     'properties': {},
                     'definitions': {},
                     'default': None,
                     'examples': {},
                     'type': 'object',
                     'required': []}
    basic_imports = ["import traitlets as T",
                     "from . import jstraitlets as jst",
                     "from .baseobject import BaseObject"]

    def __init__(self, schema, context=None, parent=None, name=None, metadata=None):
        self.schema = schema
        self.parent = parent
        self.name = name
        self.metadata = metadata or {}

        # if context is not given, then assume this is a root instance that
        # defines its context
        self.context = context or schema

    def copy(self):
        return self.__class__(schema=self.schema, context=self.context,
                              parent=self.parent, name=self.name,
                              metadata=self.metadata)

    def make_child(self, schema, name=None, metadata=None):
        """
        Make a child instance, appropriately defining the parent and context
        """
        return self.__class__(schema, context=self.context,
                              parent=self, name=name, metadata=metadata)

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
        return self.type != 'object' and not self.is_reference

    @property
    def is_object(self):
        return self.type == 'object' and not self.is_reference

    @property
    def is_reference(self):
        return '$ref' in self.schema

    @property
    def classname(self):
        if self.name:
            return self.name
        elif self.is_root:
            return "RootInstance"
        elif self.is_reference:
            return self.schema['$ref'].split('/')[-1]
        else:
            raise NotImplementedError("Anonymous class name")

    @property
    def modulename(self):
        return self.classname.lower()

    @property
    def filename(self):
        return self.modulename + '.py'

    @property
    def baseclass(self):
        return "BaseObject"

    @property
    def import_statement(self):
        return f"from .{self.modulename} import {self.classname}"

    @property
    def imports(self):
        imports = []
        imports.extend(self.basic_imports)
        for obj in self.wrapped_properties().values():
            if obj.is_reference:
                ref = self.get_reference(obj.schema['$ref'])
                if ref.is_object:
                    imports.append(ref.import_statement)
        return imports

    @property
    def module_imports(self):
        imports = []
        for obj in self.wrapped_definitions().values():
            if obj.is_object:
                imports.append(obj.import_statement)
        return imports

    def wrapped_definitions(self):
        """Return definition dictionary wrapped as JSONSchema objects"""
        return {name.lower(): self.make_child(schema, name=name)
                for name, schema in self.definitions.items()}

    def wrapped_properties(self):
        """Return property dictionary wrapped as JSONSchema objects"""
        return {name: self.make_child(val, metadata={'required': name in self.required})
                for name, val in self.properties.items()}

    def get_reference(self, ref, cache=True):
        """
        Get the JSONSchema object for the given reference code.

        Reference codes should look something like "#/definitions/MyDefinition"

        By default, this will cache objects accessed by their ref code.
        """
        if cache and ref in self._cached_references:
            return self._cached_references[ref]

        path = ref.split('/')
        name = path[-1]
        if path[0] != '#':
            raise ValueError(f"Unrecognized $ref format: '{ref}'")
        try:
            schema = self.context
            for key in path[1:]:
                schema = schema[key]
        except KeyError:
            raise ValueError(f"$ref='{ref}' not present in the schema")

        wrapped_schema = self.make_child(schema, name=name)
        if cache:
            self._cached_references[ref] = wrapped_schema
        return wrapped_schema

    def _simple_trait_code(self, typecode, kwargs):
        assert typecode in self.simple_types

        info = self.traitlet_map[typecode]
        cls = info['cls']
        args = info.get('args', ())
        kwargs.update(info.get('kwargs', {}))
        keys = info.get('validation_keys', ())
        kwargs.update({key: self.schema[key]
                       for key in keys
                       if key in self.schema})
        return construct_function_call(cls, *args, **kwargs)

    def _compound_trait_code(self, typecode, kwargs):
        assert isinstance(typecode, list)

        for typ in typecode:
            assert typ in self.simple_types
        if 'null' in typecode:
            kwargs['allow_none'] = True
        typecode = [typ for typ in typecode if typ != 'null']
        if len(typecode) == 1:
            return self._simple_trait_code(typecode[0], kwargs)
        else:
            item_kwargs = {key:val for key, val in kwargs.items()
                           if key not in ['allow_none', 'allow_undefined']}
            arg = "[{0}]".format(', '.join(self._simple_trait_code(typ, item_kwargs)
                                           for typ in typecode))
            return construct_function_call('jst.JSONUnion', Variable(arg), **kwargs)

    def _ref_trait_code(self, typecode, kwargs):
        assert '$ref' in self.schema

        ref = self.get_reference(self.schema['$ref'])
        if ref.is_object:
            return construct_function_call('jst.JSONInstance',
                                           Variable(ref.classname),
                                           **kwargs)
        else:
            ref = ref.copy()  # TODO: maybe can remove this?
            ref.metadata = self.metadata
            return ref.trait_code

    def _enum_trait_code(self, typecode, kwargs):
        assert 'enum' in self.schema
        return construct_function_call('jst.JSONEnum', self.schema["enum"],
                                       **kwargs)

    def _array_trait_code(self, typecode, kwargs):
        assert typecode == 'array'
        # TODO: fix items and implement additionalItems
        items = self.schema['items']
        if 'minItems' in self.schema:
            kwargs['minlen'] = self.schema['minItems']
        if 'maxItems' in self.schema:
            kwargs['maxlen'] = self.schema['maxItems']
        if 'uniqueItems' in self.schema:
            kwargs['uniqueItems'] = self.schema['uniqueItems']
        if isinstance(items, list):
            # TODO: need to implement this in the JSONArray traitlet
            # Also need to check value of "additionalItems"
            raise NotImplementedError("'items' keyword as list")
        else:
            itemtype = self.make_child(items).trait_code
        return construct_function_call('jst.JSONArray', Variable(itemtype),
                                       **kwargs)

    def _anyOf_trait_code(self, typecode, kwargs):
        assert 'anyOf' in self.schema
        children = [Variable(self.make_child(schema).trait_code)
                    for schema in self.schema['anyOf']]
        return construct_function_call('jst.JSONAnyOf', Variable(children),
                                       **kwargs)

    def _allOf_trait_code(self, typecode, kwargs):
        assert 'allOf' in self.schema
        children = [Variable(self.make_child(schema).trait_code)
                    for schema in self.schema['allOf']]
        return construct_function_call('jst.JSONAllOf', Variable(children),
                                       **kwargs)

    def _oneOf_trait_code(self, typecode, kwargs):
        assert 'oneOf' in self.schema
        children = [Variable(self.make_child(schema).trait_code)
                    for schema in self.schema['oneOf']]
        return construct_function_call('jst.JSONOneOf', Variable(children),
                                       **kwargs)

    def _not_trait_code(self, typecode, kwargs):
        assert 'not' in self.schema
        not_this = self.make_child(self.schema['not']).trait_code
        return construct_function_call('jst.JSONNot', Variable(not_this),
                                       **kwargs)

    @property
    def trait_code(self):
        """Create the trait code for the given typecode"""
        typecode = self.type
        if self.metadata.get('required', False):
            kwargs = {'allow_undefined': False}
        else:
            kwargs = {}

        # TODO: handle multiple entries...

        if "not" in self.schema:
            return self._not_trait_code(typecode, kwargs)
        elif "$ref" in self.schema:
            return self._ref_trait_code(typecode, kwargs)
        elif "anyOf" in self.schema:
            return self._anyOf_trait_code(typecode, kwargs)
        elif "allOf" in self.schema:
            return self._allOf_trait_code(typecode, kwargs)
        elif "oneOf" in self.schema:
            return self._oneOf_trait_code(typecode, kwargs)
        elif "enum" in self.schema:
            return self._enum_trait_code(typecode, kwargs)
        elif typecode in self.simple_types:
            return self._simple_trait_code(typecode, kwargs)
        elif typecode == 'array':
            return self._array_trait_code(typecode, kwargs)
        elif typecode == 'object':
            raise NotImplementedError("Anonymous Objects")
        elif isinstance(typecode, list):
            return self._compound_trait_code(typecode, kwargs)
        else:
            raise ValueError(f"unrecognized type identifier: {typecode}")

    def object_code(self):
        """Return code to define a BaseObject for this schema"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return jinja2.Template(self.object_template).render(cls=self, date=now)

    def module_spec(self):
        """Return the JSON specification of the module

        This can be passed to ``altair_parser.utils.load_dynamic_module``
        or to ``altair_parser.utils.save_module``

        """
        assert self.is_root
        submodroot = self.classname.lower()

        modspec = {
            'jstraitlets.py': open(os.path.join(os.path.dirname(__file__),
                                   'src', 'jstraitlets.py')).read(),
            'baseobject.py': open(os.path.join(os.path.dirname(__file__),
                                  'src', 'baseobject.py')).read(),
            self.filename: self.object_code()
        }

        modspec['__init__.py'] = '\n'.join([self.import_statement]
                                            + self.module_imports)

        modspec.update({schema.filename: schema.object_code()
                        for schema in self.wrapped_definitions().values()
                        if schema.is_object})

        return modspec
