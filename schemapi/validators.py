"""Objects that implement schema validation"""

import warnings
import re

from .utils import isnumeric

class SchemaValidationError(Exception):
    pass


class ValidatorList(list):
    """Instantiate a list of validators given a JSONSchema

    Parameters
    ----------
    obj : JSONSchema object
        The schema object from which to build the validators

    Methods
    -------
    validate(self, value):
        validate value with all validators in list
    """
    def __init__(self, obj):
        super(ValidatorList, self).__init__()
        validator_classes = [cls for cls in Validator.__subclasses__()
                             if cls._matches(obj.schema)]

        used_keys = {'definitions', 'description', 'title', '$schema'}
        for cls in validator_classes:
            cls_schema = {key:val for key, val in obj.schema.items()
                          if key in cls.recognized_keys}
            used_keys |= cls_schema.keys()
            self.append(cls(cls_schema, parent=obj))
        unused = obj.schema.keys() - used_keys
        if unused:
            warnings.warn("Unused keys {0} in {1}"
                          "".format(unused, self))

    def validate(self, obj):
        for validator in self:
            validator.validate(obj)


class Validator(object):
    """Abstract base class for JSONSchema validation.

    This class should not be used directly; rather use the ValidatorList class
    """
    recognized_keys = set()

    def __init__(self, schema, parent):
        self.schema = schema
        self.parent = parent

        unrecognized = set(schema.keys()) - set(self.recognized_keys)
        if unrecognized:
            warnings.warn('Unrecognized keys {0} in class {1}'
                          ''.format(unrecognized, self.__class__.__name__))

    def _init_child(self, schema):
        """Initialize a child JSONSchema object from a schema dict"""
        return self.parent.initialize_child(schema)

    def __repr__(self):
        if len(self.schema) > 3:
            args = ', '.join(sorted(self.schema.keys())[:3]) + '...'
        else:
            args = ', '.join(sorted(self.schema.keys()))
        return "{0}({1})".format(self.__class__.__name__, args)

    @classmethod
    def _matches(cls, schema):
        raise NotImplementedError()

    def validate(self, value):
        raise NotImplementedError()


class ObjectValidator(Validator):
    recognized_keys = {'type', 'properties', 'additionalProperties',
                       'patternProperties', 'required'}
    # TODO: handle pattern properties
    @classmethod
    def _matches(cls, schema):
        return (schema.get('type', None) == 'object'
                 or 'properties' in schema
                 or 'additionalProperties' in schema)

    def validate(self, obj):
        required = self.schema.get('required', [])
        if not isinstance(obj, dict):
            if self.schema.get('type', None) == 'object':
                raise SchemaValidationError("{0} is not of type='object'"
                                            "".format(obj))
            if required:
                raise SchemaValidationError("{0} is missing properties {1}"
                                            "".format(obj, required))
        if not all(key in obj for key in self.schema.get('required', [])):
            raise SchemaValidationError("{0} does not contain required keys {1}"
                                        "".format(obj, self.schema['required']))
        if isinstance(obj, dict):
            for key, val in obj.items():
                properties = self.schema.get('properties', {})
                patternProperties = self.schema.get('patternProperties', {})
                additionalProperties = self.schema.get('additionalProperties', True)
                if key in properties:
                    self._init_child(properties[key]).validate(val)
                elif patternProperties:
                    raise NotImplementedError('patternProperties validation')
                elif isinstance(additionalProperties, dict):
                    self.parent.initialize_child(additionalProperties).validate(val)
                elif not additionalProperties:
                    raise SchemaValidationError("{0} property {1} is invalid"
                                                "".format(obj, key))


class ArrayValidator(Validator):
    recognized_keys = {'type', 'items', 'minItems', 'maxItems', 'numItems'}
    @classmethod
    def _matches(cls, schema):
        return schema.get('type', None) == 'array' or 'items' in schema

    def validate(self, obj):
        if not isinstance(obj, list):
            raise SchemaValidationError()
        if 'minItems' in self.schema and len(obj) < self.schema['minItems']:
            raise SchemaValidationError()
        if 'maxItems' in self.schema and len(obj) > self.schema['maxItems']:
            raise SchemaValidationError()
        if 'numItems' in self.schema and len(obj) != self.schema['numItems']:
            raise SchemaValidationError()
        if 'items' in self.schema:
            itemtype = self._init_child(self.schema['items'])
            for val in obj:
                itemtype.validate(val)


class NumberTypeValidator(Validator):
    recognized_keys = {'type', 'minimum', 'maximum', 'default',
                       'exclusiveMinimum', 'exclusiveMaximum'}
    @classmethod
    def _matches(cls, schema):
        return schema.get('type', None) == 'number'

    def validate(self, obj):
        if not isnumeric(obj):
            raise SchemaValidationError("{0} is not a numeric type"
                                        "".format(obj))
        if 'minimum' in self.schema and obj < self.schema['minimum']:
            raise SchemaValidationError("{0} is less than minimum={1}"
                                        "".format(obj, self.schema['minimum']))
        if 'maximum' in self.schema and obj > self.schema['maximum']:
            raise SchemaValidationError("{0} is greater than maximum={1}"
                                        "".format(obj, self.schema['maximum']))
        if 'exclusiveMinimum' in self.schema and obj <= self.schema['exclusiveMinimum']:
            raise SchemaValidationError("{0} is less than exclusiveMinimum={1}"
                                        "".format(obj, self.schema['exclusiveMinimum']))
        if 'exclusiveMaximum' in self.schema and obj >= self.schema['exclusiveMaximum']:
            raise SchemaValidationError("{0} is greater than exclusiveMaximum={1}"
                                        "".format(obj, self.schema['exclusiveMaximum']))


class IntegerTypeValidator(Validator):
    recognized_keys = {'type', 'mimimum', 'maximum', 'default',
                       'exclusiveMinimum', 'exclusiveMaximum'}
    @classmethod
    def _matches(cls, schema):
        return schema.get('type', None) == 'integer'

    def validate(self, obj):
        if not isnumeric(obj):
            raise SchemaValidationError("{0} is not a numeric type"
                                        "".format(obj))
        if not int(obj) == obj:
            raise SchemaValidationError("{0} is not an integer".format(obj))
        if 'minimum' in self.schema and obj < self.schema['minimum']:
            raise SchemaValidationError("{0} is less than minimum={1}"
                                        "".format(obj, self.schema['minimum']))
        if 'maximum' in self.schema and obj > self.schema['maximum']:
            raise SchemaValidationError("{0} is greater than maximum={1}"
                                        "".format(obj, self.schema['maximum']))
        if 'exclusiveMinimum' in self.schema and obj <= self.schema['exclusiveMinimum']:
            raise SchemaValidationError("{0} is less than exclusiveMinimum={1}"
                                        "".format(obj, self.schema['exclusiveMinimum']))
        if 'exclusiveMaximum' in self.schema and obj >= self.schema['exclusiveMaximum']:
            raise SchemaValidationError("{0} is greater than exclusiveMaximum={1}"
                                        "".format(obj, self.schema['exclusiveMaximum']))


class StringTypeValidator(Validator):
    recognized_keys = {'type', 'pattern', 'format',
                       'minLength', 'maxLength', 'default'}
    valid_formats = ['date-time', 'email', 'hostname', 'ipv4', 'ipv6', 'uri']
    @classmethod
    def _matches(cls, schema):
        return schema.get('type', None) == 'string'

    def validate(self, obj):
        if not isinstance(obj, str):
            raise SchemaValidationError("{0} is not a string".format(obj))
        if 'minLength' in self.schema and len(obj) < self.schema['minLength']:
            raise SchemaValidationError("{0} is shorter than minLength={1}"
                                        "".format(obj, self.schema['minLength']))
        if 'maxLength' in self.schema and len(obj) > self.schema['maxLength']:
            raise SchemaValidationError("{0} is longer than maxLength={1}"
                                        "".format(obj, self.schema['maxLength']))
        if 'pattern' in self.schema and not re.match(self.schema['pattern'], obj):
            raise SchemaValidationError("{0} does not match pattern {1}"
                                        "".format(obj, self.schema['pattern']))
        if 'format' in self.schema:
            if self.schema['format'] not in self.valid_formats:
                raise SchemaValidationError('format not recognized')
            warnings.warn("format constraint not implemented in StringTypeValidator")


class NullTypeValidator(Validator):
    recognized_keys = {'type'}
    @classmethod
    def _matches(cls, schema):
        return schema.get('type', None) == 'null'

    def validate(self, obj):
        if obj is not None:
            raise SchemaValidationError()


class BooleanTypeValidator(Validator):
    recognized_keys = {'type', 'default'}
    @classmethod
    def _matches(cls, schema):
        return schema.get('type', None) == 'boolean'

    def validate(self, obj):
        if not isinstance(obj, bool):
            raise SchemaValidationError()


class EnumValidator(Validator):
    recognized_keys = {'enum', 'default'}
    @classmethod
    def _matches(cls, schema):
        return 'enum' in schema

    def validate(self, obj):
        print(obj, self.schema['enum'], obj in self.schema['enum'])
        if obj not in self.schema['enum']:
            raise SchemaValidationError()


class MultiTypeValidator(Validator):
    recognized_keys = {'type', 'minimum', 'maximum'}
    @classmethod
    def _matches(cls, schema):
        return isinstance(schema.get('type', None), list)

    def validate(self, obj):
        schema_copy = self.schema.copy()
        for typ in self.schema['type']:
            schema_copy['type'] = typ
            try:
                self._init_child(schema_copy).validate(obj)
            except:
                pass
            else:
                return
        raise SchemaValidationError()


class RefValidator(Validator):
    recognized_keys = {'$ref'}

    @classmethod
    def _matches(cls, schema):
        return '$ref' in schema

    @property
    def name(self):
        return self.schema['$ref']

    @property
    def refschema(self):
        keys = self.schema['$ref'].split('/')
        if keys[0] != '#':
            raise ValueError("$ref = {0} not recognized".format(self.schema['$ref']))
        refschema = self.parent.root.schema
        for key in keys[1:]:
            refschema = refschema[key]
        return refschema

    def __repr__(self):
        return "RefValidator('{0}')".format(self.name)

    def validate(self, obj):
        self._init_child(self.refschema).validate(obj)


class AnyOfValidator(Validator):
    recognized_keys = {'anyOf'}
    @classmethod
    def _matches(cls, schema):
        return 'anyOf' in schema

    def validate(self, obj):
        for child in self.schema['anyOf']:
            print(child, obj)
            try:
                self._init_child(child).validate(obj)
            except SchemaValidationError:
                pass
            else:
                return
        raise SchemaValidationError()


class OneOfValidator(Validator):
    recognized_keys = {'oneOf'}
    @classmethod
    def _matches(cls, schema):
        return 'oneOf' in schema

    def validate(self, obj):
        count = 0
        for child in self.schema['oneOf']:
            try:
                self._init_child(child).validate(obj)
            except:
                pass
            else:
                count += 1
        if count != 1:
            raise SchemaValidationError()


class AllOfValidator(Validator):
    recognized_keys = {'allOf'}
    @classmethod
    def _matches(cls, schema):
        return 'allOf' in schema

    def validate(self, obj):
        for child in self.schema['allOf']:
            self._init_child(child).validate(obj)


class NotValidator(Validator):
    recognized_keys = {'not'}
    @classmethod
    def _matches(cls, schema):
        return 'not' in schema

    def validate(self, obj):
        try:
            self._init_child(self.schema['not']).validate(obj)
        except SchemaValidationError:
            pass
        else:
            raise SchemaValidationError()
