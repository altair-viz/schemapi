import pytest

from ... import JSONSchema
from .. import iter_schemas_with_names, load_schema


@pytest.mark.filterwarnings('ignore:format constraint')
@pytest.mark.parametrize('name,schema', iter_schemas_with_names())
def test_metaschema_validation(name, schema):
    root = JSONSchema(load_schema('jsonschema-draft04.json'))
    root.validate(schema)


#@pytest.mark.filterwarnings('ignore:Unused')
@pytest.mark.filterwarnings('ignore:format constraint')
def test_schema_validation():
    schema = JSONSchema(load_schema('vega-lite-v2.0.0.json'))

    vega_lite_bar = {
      "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
      "description": "A simple bar chart with embedded data.",
      "data": {
        "values": [
          {"a": "A","b": 28}, {"a": "B","b": 55}, {"a": "C","b": 43},
          {"a": "D","b": 91}, {"a": "E","b": 81}, {"a": "F","b": 53},
          {"a": "G","b": 19}, {"a": "H","b": 87}, {"a": "I","b": 52}
        ]
      },
      "mark": "bar",
      "encoding": {
        "x": {"field": "a", "type": "ordinal"},
        "y": {"field": "b", "type": "quantitative"}
      }
    }
    schema.validate(vega_lite_bar)

    vega_lite_github_punchcard = {
      "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
      "data": { "url": "data/github.csv"},
      "mark": "circle",
      "encoding": {
        "y": {
          "field": "time",
          "type": "ordinal",
          "timeUnit": "day"
        },
        "x": {
          "field": "time",
          "type": "ordinal",
          "timeUnit": "hours"
        },
        "size": {
          "field": "count",
          "type": "quantitative",
          "aggregate": "sum"
        }
      }
    }
    schema.validate(vega_lite_github_punchcard)
