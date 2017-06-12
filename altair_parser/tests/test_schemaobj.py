from ..schemaobj import VLSchema


SIMPLE_SCHEMA = {
    '$ref': '#/definitions/TopLevel',
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'definitions': {
        'TopLevel': {
            'enum': ['a', 'b', 'c']
        }
    }
}



def test_simple_schema():
    schema = VLSchema(SIMPLE_SCHEMA)
    assert len(schema.definitions) == 1
