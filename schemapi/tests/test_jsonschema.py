import pytest

import traitlets as T

from .. import JSONSchema
from ..utils import load_dynamic_module


@pytest.mark.parametrize('spec,output',
                         [({'type': 'string'}, 'jst.JSONString()'),
                          ({'type': 'boolean'}, 'jst.JSONBoolean()'),
                          ({'type': 'number'}, 'jst.JSONNumber()'),
                          ({'type': 'null'}, 'jst.JSONNull()'),
                          ({'type': ['string', 'number']},
                           'jst.JSONUnion([jst.JSONString(), jst.JSONNumber()])'),
                          ({'type': ['string', 'null']},
                            'jst.JSONString(allow_none=True)'),
                           ({'type': ['string', 'number', 'null']},
                             'jst.JSONUnion([jst.JSONString(), jst.JSONNumber()], allow_none=True)'),
                          ({'type': 'array', 'items': {'type': 'string'}},
                           'jst.JSONArray(jst.JSONString())'),
                          ({'anyOf': [{'type': 'integer'}, {'type': 'string'}]},
                           "jst.JSONAnyOf([jst.JSONInteger(), jst.JSONString()])"),
                          ({'allOf': [{'type': 'integer'}, {'type': 'string'}]},
                           "jst.JSONAllOf([jst.JSONInteger(), jst.JSONString()])"),
                          ({'oneOf': [{'type': 'integer'}, {'type': 'string'}]},
                           "jst.JSONOneOf([jst.JSONInteger(), jst.JSONString()])")])
def test_trait_code(spec, output):
    assert JSONSchema(spec).trait_code == output


def test_required_keyword():
    schema = {
        'type': 'object',
        'definitions': {
            'positiveInteger': {'type': 'integer', 'minimum': 0},
            'twoNumbers': {'properties': {'num1': {'type': 'number'},
                                          'num2': {'type': 'number'}}}
        },
        'properties': {
            'string1': {'type': 'string'},
            'string2': {'type': 'string'},
            'integer1': {'type': 'integer'},
            'integer2': {'type': 'integer'},
            'number1': {'type': 'number'},
            'number2': {'type': 'number'},
            'bool1': {'type': 'boolean'},
            'bool2': {'type': 'boolean'},
            'null1': {'type': 'null'},
            'null2': {'type': 'null'},
            'enum1': {'enum': [1, 2, 3]},
            'enum2': {'enum': [1, 2, 3]},
            'array1': {'type': 'array', 'items': {'type': 'integer'}},
            'array2': {'type': 'array', 'items': {'type': 'integer'}},
            'traitref1': {'$ref': '#/definitions/positiveInteger'},
            'traitref2': {'$ref': '#/definitions/positiveInteger'},
            'objref1': {'$ref': '#/definitions/twoNumbers'},
            'objref2': {'$ref': '#/definitions/twoNumbers'},
            'typelist1': {'type': ['string', 'integer']},
            'typelist2': {'type': ['string', 'integer']},
        },
        'required': ['string1', 'integer1', 'number1',
                     'bool1', 'null1', 'enum1', 'array1',
                     'traitref1', 'objref1', 'typelist1']
    }
    js = JSONSchema(schema)

    load_dynamic_module('_schema', js.source_tree(), reload_module=True)
    from _schema import jstraitlets as jst
    from _schema import Root

    # Required for the eval-based tests below
    def _localname(name):
        return "{0}.{1}".format(__name__, name)

    assert Root()._required_traits == js.required

    r = Root()
    with pytest.raises(T.TraitError) as err:
        r.to_dict()
    assert err.match("Required trait '[a-z]+1' is undefined")


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
        definition_code = '#/definitions/{name}'.format(name=name)

        obj1 = js.get_reference(definition_code)
        obj2 = JSONSchema(definition)
        assert obj1.trait_code == obj2.trait_code
