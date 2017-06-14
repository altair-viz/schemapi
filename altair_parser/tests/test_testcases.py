
import traitlets as T
import jsonschema
import pytest

from .. import JSONSchema
from .. import testcases


ALL_TESTCASES = testcases.all()


@pytest.mark.parametrize('testcase', ALL_TESTCASES.keys())
def test_testcases_jsonschema(testcase):
    testcase = ALL_TESTCASES[testcase]

    schema = testcase['schema']
    valid = testcase['valid']
    invalid = testcase.get('invalid', [])

    for instance in valid:
        jsonschema.validate(instance, schema)
    for instance in invalid:
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, schema)


@pytest.mark.parametrize('testcase', ALL_TESTCASES.keys())
def test_testcases_traitlets(testcase):
    testcase = ALL_TESTCASES[testcase]
    
    schema = testcase['schema']
    valid = testcase['valid']
    invalid = testcase.get('invalid', [])

    traitlets_obj = JSONSchema(schema)
    exec(traitlets_obj.object_code(), globals())

    for instance in valid:
        RootInstance(**instance)
    for instance in invalid:
        with pytest.raises(T.TraitError):
            RootInstance(**instance)
