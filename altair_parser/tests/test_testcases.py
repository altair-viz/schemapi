
import traitlets as T
import jsonschema
import pytest

from .. import JSONSchema
from . import _testcases

testcases = {key: getattr(_testcases, key)
             for key in dir(_testcases)
             if not key.startswith('__')}


@pytest.mark.parametrize('testcase', testcases.keys())
def test_testcases_jsonschema(testcase):
    testcase = testcases[testcase]

    schema = testcase['schema']
    valid = testcase['valid']
    invalid = testcase.get('invalid', [])

    for instance in valid:
        jsonschema.validate(instance, schema)
    for instance in invalid:
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, schema)


@pytest.mark.parametrize('testcase', testcases.keys())
def test_testcases_traitlets(testcase):
    testcase = testcases[testcase]

    schema = testcase['schema']
    valid = testcase['valid']
    invalid = testcase.get('invalid', [])

    traitlets_obj = JSONSchema(schema)
    locals = {}
    exec(traitlets_obj.object_code(), locals)
    RootInstance = locals['RootInstance']

    for instance in valid:
        RootInstance(**instance)
    for instance in invalid:
        with pytest.raises(T.TraitError):
            RootInstance(**instance)
