import pytest
from schemapi import SchemaBase, module_code


@pytest.fixture
def schema():
    return {
        'definitions': {
            'Person': {
                'properties': {
                    'name': {'type': 'string'},
                    'age': {'type': 'integer'},
                }
            }
        },
        'additionalProperties'
        'properties': {
            'people': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Person'}
            }
        }
    }


def test_module_code(schema):
    code = module_code(schema, root_name='Family')

    namespace = {}
    exec(code, namespace)

    Family = namespace['Family']
    Person = namespace['Person']

    assert issubclass(Family, SchemaBase)
    assert issubclass(Person, SchemaBase)

    family = Family(people=[Person(name='Alice', age=25), Person(name='Bob', age=26)])
    dct = family.to_dict()
    assert dct == {'people': [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 26}]}
    family2 = Family.from_dict(dct)
    assert family2.to_dict() == dct