import pytest
from schemapi import SchemaBase, SchemaModuleGenerator


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
        'properties': {
            'family_name': {
                'type': 'string'
            },
            'people': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Person'}
            }
        },
        'required': ['family_name']
    }


def test_module_code(schema):
    gen = SchemaModuleGenerator(schema, root_name='Family')
    code = gen.module_code()

    namespace = {}
    exec(code, namespace)

    Family = namespace['Family']
    Person = namespace['Person']

    assert issubclass(Family, SchemaBase)
    assert issubclass(Person, SchemaBase)

    family = Family(family_name='Smith', people=[Person(name='Alice', age=25), Person(name='Bob', age=26)])
    dct = family.to_dict()
    assert dct == {'family_name': 'Smith', 'people': [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 26}]}
    family2 = Family.from_dict(dct)
    assert family2.to_dict() == dct


def test_dynamic_module(schema):
    gen = SchemaModuleGenerator(schema, root_name='Family')
    testmod = gen.import_as('testmod')
    assert issubclass(testmod.Family, SchemaBase)
    assert issubclass(testmod.Person, SchemaBase)

    from testmod import Family, Person
    assert issubclass(Family, SchemaBase)
    assert issubclass(Person, SchemaBase)

    family = Family(family_name='Smith', people=[Person(name='Alice', age=25), Person(name='Bob', age=26)])
    dct = family.to_dict()
    assert dct == {'family_name': 'Smith', 'people': [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 26}]}
    family2 = Family.from_dict(dct)
    assert family2.to_dict() == dct