"""Test ability to wrap schemas in the schemapi/schemas directory"""

import os
import pytest
import json

import jsonschema

from ... import JSONSchema
from .. import iter_schemas_with_names, load_schema


@pytest.mark.parametrize('name,schema', iter_schemas_with_names())
def test_schema_jsonschema(name, schema):
    """Sanity check: test that the schema is a valid jsonschema"""
    metaschema = load_schema('jsonschema-draft04.json')
    jsonschema.validate(schema, metaschema)


@pytest.mark.parametrize('name,schema', iter_schemas_with_names())
def test_parse_schema(name, schema):
    """Test parsing the entire schema"""
    if name == 'vega-v3.0.7.json':
        pytest.xfail("vega schema has unsupported elements")
    modulename = '_schema'
    obj = JSONSchema(schema)
    obj.load_module(modulename, reload_module=True)
