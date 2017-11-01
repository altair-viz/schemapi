import pytest
from .. import JSONSchema, SchemaValidationError
from .. import validators as val


def generate_simple_schemas():
    yield ({'type': 'integer'}, [val.IntegerTypeValidator])
    yield ({'type': 'number'}, [val.NumberTypeValidator])
    yield ({'type': 'string'}, [val.StringTypeValidator])
    yield ({'type': 'null'}, [val.NullTypeValidator])
    yield ({'type': 'array'}, [val.ArrayValidator])
    yield ({'type': 'object'}, [val.ObjectValidator])
    yield ({'type': ['integer', 'number', 'string']}, [val.MultiTypeValidator])
    yield ({'properties': {'foo': {'type': 'string'}}}, [val.ObjectValidator])
    yield ({'additionalProperties': {'type': 'string'}}, [val.ObjectValidator])
    yield ({'enum': ['hello'], 'type': 'string'}, [val.EnumValidator,
                                                   val.StringTypeValidator])
    yield ({'enum': [0, 1], 'type': 'integer'}, [val.EnumValidator,
                                                 val.IntegerTypeValidator])
    yield ({'enum': [0, 1], 'type': 'number'}, [val.EnumValidator,
                                                val.NumberTypeValidator])
    yield ({'enum': [True], 'type': 'boolean'}, [val.EnumValidator,
                                                 val.BooleanTypeValidator])
    yield ({'enum': [None], 'type': 'null'}, [val.EnumValidator,
                                              val.NullTypeValidator])
    yield ({'enum': ['hello', None, 2]}, [val.EnumValidator])
    yield ({'description': 'foo'}, [])
    yield ({}, [])
    yield ({'$ref': '#/definitions/blah',
            'definitions': {'blah': {'type': 'string'}}},
           [val.RefValidator])
    yield({'anyOf': [{'type': 'integer'}, {'type': 'string'}]},
          [val.AnyOfValidator])


@pytest.mark.parametrize('schema, vclasses', generate_simple_schemas())
def test_simple_schemas(schema, vclasses):
    root = JSONSchema(schema)
    assert len(root.validators) == len(vclasses)
    for v in root.validators:
        assert isinstance(v, tuple(vclasses))

    schema['$schema'] = 'http://foo.com/schema.json/#'
    schema['description'] = 'this is a description'
    root = JSONSchema(schema)
    assert len(root.validators) == len(vclasses)
    for v in root.validators:
        assert isinstance(v, tuple(vclasses))


def schemas_for_validation():
    # yield tuples of (schema, valid_values, invalid_values)
    yield ({"type": "number"},
           [1, 2.5], [True, None, 'hello'])
    yield ({"type": "integer"},
           [1, 2.0], [True, None, 'hello', 2.5])
    yield ({"type": "string"},
           ["", 'hello'], [True, None, 1, 2.5])
    yield ({"type": "boolean"},
           [True, False], ['hello', None, 1, 2.5])
    yield ({"type": "null"},
           [None], ['hello', True, 1, 2.5])
    yield ({"type": ["boolean", "integer", "string"]},
           [True, 4.0, 'hello'], [None, 4.5, {}])
    yield ({"type": "array", 'items': {}},
           [[1,'hello'], [None, True]], [1, 'hello'])
    yield ({"type": "array", 'items': {'type': 'number'}},
           [[1,2], [0.1, 2.5]], [[2.0, 'hello'], [1, None]])
    yield ({"enum": [5, "hello", None, False]},
           [5, "hello", None, False], [2, 'blah', True])
    yield ({"type": "string", "enum": ['a', 'b', 'c']},
           ['a', 'b', 'c'], [2, 'blah', True])
    yield ({"type": "number", "minimum": 0, "maximum": 1},
           [0, 0.5, 1], [-1, 2])
    yield ({"type": "number", "exclusiveMinimum": 0, "exclusiveMaximum": 1},
           [0.01, 0.5, 0.99], [0, 1])
    yield ({"type": "string", 'minLength': 2, 'maxLength': 5},
           ["12", "123", "12345"], ["", "1", "123456"])
    yield ({"type": "string", "pattern": "^[a-zA-Z1-9]+$"},
           ['abc', 'ABc2', 'Zxy4'], ['', '1-9', 'A&4'])
    yield ({'type': 'object', 'properties': {'a': {'type': 'integer'}}},
           [{'a':4}, {'a':0, 'b':5}], [1, {'a':'foo'}, None])
    yield ({'properties': {'a': {'type': 'integer'}},
            'additionalProperties': False},
           [{'a':4}, 1, None], [{'a':'foo'}, {'a':0, 'b':5}])
    yield ({'type': 'object'},
           [{}, {'a':4}, {'a':0, 'b':5}], [1, 'blah', None])
    yield ({'type': 'object', 'additionalProperties': False},
           [{}], [{'a':4}, {'a':0, 'b':5}])
    yield ({'type': 'object', 'additionalProperties': {'type': 'string'}},
           [{'a': 'foo'}, {'a': 'blah', 'b': 'hello'}],
           [{'a':4}, {'a':0, 'b':5}])
    yield ({'$ref': '#/definitions/Foo',
            'definitions': {'Foo': {'type': 'string'}}},
           ['a', 'b', 'c'], [1, None, False])
    yield({'anyOf': [{'type': 'integer'}, {'type': 'object'}]},
          [1, {}, {'foo': 'bar'}], ['hello', None])
    yield({'allOf': [{'properties': {'a': {'type': 'integer'}}, 'required': ['a']},
                     {'properties': {'b': {'type': 'string'}}}]},
          [{'a': 1}, {'a': 1, 'b': '2'}], [{'b': 'yo'}, 4, None])
    yield({'oneOf': [{'type': 'integer'}, {'type': 'number'}, {'type': 'object'}]},
          [1.5, {'foo': 'bar'}], [1.0, 'hello', None])
    yield({'not': {'type': 'integer'}},
          [1.5, 'blah', None], [1, 2.0])


@pytest.mark.parametrize('schema,valid,invalid', schemas_for_validation())
def test_simple_validation(schema, valid, invalid):
    schemaobj = JSONSchema(schema)

    for value in valid:
        schemaobj.validate(value)

    for value in invalid:
        with pytest.raises(SchemaValidationError):
            schemaobj.validate(value)
