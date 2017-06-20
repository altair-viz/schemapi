import pytest
from .. import JSONSchema


@pytest.mark.parametrize('spec,output',
                         [({'type': 'string'}, 'jst.JSONString()'),
                          ({'type': 'boolean'}, 'jst.JSONBoolean()'),
                          ({'type': 'number'}, 'jst.JSONNumber()'),
                          ({'type': 'null'}, 'jst.JSONNull()'),
                          ({'type': ['string', 'number']},
                           'jst.JSONUnion([jst.JSONString(), jst.JSONNumber()])'),
                          ({'type': 'array', 'items': {'type': 'string'}},
                           'jst.JSONArray(jst.JSONString())'),
                          ({'enum': [None, 42, "hello"]},
                           "jst.JSONEnum([None, 42, 'hello'])")])
def test_trait_code(spec, output):
    assert JSONSchema(spec).trait_code == output


def test_get_reference():
    schema = {
        'definitions': {
            'MyString': {
                'type': 'string'
            },
            'IntOrNone': {
                'type': ['integer', 'null']
            }
        }
    }

    js = JSONSchema(schema)
    for name, definition in schema['definitions'].items():
        definition_code = f'#/definitions/{name}'

        obj1 = js.get_reference(definition_code)
        obj2 = JSONSchema(definition)
        assert obj1.trait_code == obj2.trait_code

        obj3 = js.get_reference(definition_code)
        assert obj1 is obj3  # Make sure reference cacheing works correctly
