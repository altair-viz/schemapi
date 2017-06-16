import pytest
from .. import JSONSchema


@pytest.mark.parametrize('spec,output',
                         [({'type': 'string'}, 'jst.JSONString()'),
                          ({'type': 'boolean'}, 'jst.JSONBoolean()'),
                          ({'type': 'number'}, 'jst.JSONNumber()'),
                          ({'type': 'null'}, 'jst.JSONNull()'),
                          ({'type': ['string', 'number']},
                           'jst.JSONUnion([jst.JSONString(), jst.JSONNumber()])')])
def test_trait_code(spec, output):
    assert JSONSchema(spec).trait_code == output
