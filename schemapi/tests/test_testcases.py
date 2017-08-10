"""
These tests iterate through the examples defined in _testcases.py and make
sure each passes with both schemapi and jsonschema
"""

import traitlets as T
import jsonschema
import pytest

from .. import JSONSchema
from . import _testcases

testcases = {key: getattr(_testcases, key)
             for key in dir(_testcases)
             if not key.startswith('_')}


@pytest.mark.parametrize('testcase', testcases.keys())
def test_testcases_jsonschema(testcase):
    testcase = testcases[testcase]

    schema = testcase['schema']
    valid = testcase.get('valid', [])
    invalid = testcase.get('invalid', [])

    for instance in valid:
        jsonschema.validate(instance, schema)
    for instance in invalid:
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, schema)


@pytest.mark.parametrize('testcase', testcases.keys())
def test_testcases_traitlets(testcase):
    testcase = testcases[testcase]
    modulename = '_schema'

    schema = testcase['schema']
    valid = testcase.get('valid', [])
    invalid = testcase.get('invalid', [])

    traitlets_obj = JSONSchema(schema)

    for key, code in traitlets_obj.source_tree().items():
        if key in ['jstraitlets.py', 'tests']:
            continue
        # Print code here... useful for debugging when errors happen
        print(70 * '#')
        print(code)
        print()

    schema = traitlets_obj.load_module(modulename, reload_module=True)

    for instance in valid:
        schema.Root.from_dict(instance)
    for instance in invalid:
        with pytest.raises(T.TraitError):
            r = schema.Root.from_dict(instance)
            r.to_dict()  # catches unfilled requirements


@pytest.mark.parametrize('testcase', testcases.keys())
def test_dict_round_trip(testcase):
    testcase = testcases[testcase]
    modulename = '_schema'

    schema = testcase['schema']
    valid = testcase.get('valid', [])

    traitlets_obj = JSONSchema(schema)

    for key, code in traitlets_obj.source_tree().items():
        if key in ['jstraitlets.py', 'tests']:
            continue
        # Print code here... useful for debugging when errors happen
        print(70 * '#')
        print(code)
        print()

    schema = traitlets_obj.load_module(modulename, reload_module=True)

    for instance in valid:
        obj = schema.Root.from_dict(instance)
        assert obj.to_dict() == instance
