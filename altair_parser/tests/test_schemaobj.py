import os

from ..schemaobj import VegaSchema


SIMPLE_SCHEMA = {
    '$ref': '#/definitions/TopLevel',
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'definitions': {
        'TopLevel': {
            'properties': {'foo':
                {'description': "foo property",
                 'type': 'number'}}
        }
    }
}



def test_simple_schema():
    schema = VegaSchema(SIMPLE_SCHEMA)
    assert len(schema.definitions) == 1

    for name, definition in schema.definitions.items():
        assert definition.name == name
        for name, prop in definition.properties.items():
            assert prop.name == name
            assert prop.type == 'number'
            assert prop.description == "foo property"


def test_vegalite_schema():
    filename = os.path.join(os.path.dirname(__file__), '..',
                            'schemas', 'vega-lite-v2.0.0.json')
    schema = VegaSchema.from_file(filename)
    for name, definition in schema.definitions.items():
        assert definition.name == name
        for name, prop in definition.properties.items():
            assert prop.name == name
