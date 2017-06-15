import pytest
from .. import JSONSchema


@pytest.mark.parametrize('typecode,output',
                         [('string', 'T.Unicode()'),
                          ('boolean', 'T.Bool()'),
                          ('number', 'T.Float()'),
                          ('null',
                           'T.Integer(allow_none=True, minimum=1, maximum=0)'),
                          (['string', 'number'],
                           'T.Union([T.Unicode(), T.Float()])')])
def test_trait_code(typecode, output):
    assert JSONSchema._get_trait_code(typecode) == output
    
