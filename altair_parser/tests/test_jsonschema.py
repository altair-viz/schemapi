import pytest
from .. import JSONSchema


@pytest.mark.parametrize('typecode,output',
                         [('string', 'jst.JSONString()'),
                          ('boolean', 'jst.JSONBoolean()'),
                          ('number', 'jst.JSONNumber()'),
                          ('null', 'jst.JSONNull()'),
                          (['string', 'number'],
                           'jst.JSONUnion([jst.JSONString(), jst.JSONNumber()])')])
def test_trait_code(typecode, output):
    assert JSONSchema._get_trait_code(typecode) == output
