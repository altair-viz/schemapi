"""Basic unit tests for JSONSchema"""
from .. import JSONSchema

schema = {
    'definitions': {
        'PositiveInteger': {'type': 'integer', 'minimum': 0},
        'LongString': {'type': 'string', 'minLength': 10},
        'Unused': {'type': 'null'}
    },
    'type': 'object',
    'properties': {
        'i': {'$ref': '#/definitions/PositiveInteger'},
        's': {'$ref': '#/definitions/LongString'}
    }
}

def test_definitions():
    schemaobj = JSONSchema(schema, root_name='MyRoot')
    assert schemaobj.definitions.keys() == {'MyRoot',
                                            'PositiveInteger',
                                            'LongString'}

    for name, subschema in schemaobj.definitions.items():
        if name == 'MyRoot':
            assert subschema == schema
        else:
            assert schema['definitions'][name] == subschema
