import pytest

from ... import JSONSchema
from .. import iter_schemas_with_names

num_schemas = {'jsonschema-draft04.json': 29,
               'vega-v3.0.7.json': 631,
               'vega-lite-v1.2.json': 309,
               'vega-lite-v2.0.json': 645}

num_definitions = {'jsonschema-draft04.json': 6,
                   'vega-v3.0.7.json': 106,
                   'vega-lite-v1.2.json': 54,
                   'vega-lite-v2.0.json': 150}


@pytest.mark.filterwarnings('ignore:Unused')
@pytest.mark.parametrize('name,schema', iter_schemas_with_names())
def test_load_full_schemas(name, schema):
    root = JSONSchema(schema)
    assert len(root._registry) == num_schemas.get(name, None)
    assert len(root._definitions) == num_definitions.get(name, None)
