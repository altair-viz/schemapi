import random

import pytest

from .. import hash_schema, regularize_name, trait_name_map, sorted_repr


def generate_schemas():
    yield 4
    yield 3.14
    yield 'foo'
    yield None
    yield {'a': 1, 'b': 2}
    yield [1, 2, 3]
    yield {1, 2, 3}
    yield (1, 2, 3)
    yield {
        'a': {
            'key': [1, 2, 3],
            'val': {'a', 'b', 'c'}
            },
        'b': [{}, {'name': 'bob', 'age': 31}],
        'c': (1, 2, 3)
    }


def scramble(val):
    if isinstance(val, dict):
        L = [(k, scramble(v)) for k, v in val.items()]
        random.shuffle(L)
        return dict(L)
    elif isinstance(val, set):
        L = [scramble(v) for v in val]
        random.shuffle(L)
        return set(L)
    elif isinstance(val, tuple):
        return tuple(map(scramble, val))
    elif isinstance(val, list):
        return list(map(scramble, val))
    else:
        return val


@pytest.mark.parametrize('schema', generate_schemas())
def test_hash_schema(schema):
    """Test that schemas compile correctly, even when order is changed"""
    hsh = hash_schema(schema)
    assert all(hash_schema(scramble(schema)) == hsh for i in range(10))


def test_regularize_name():
    assert regularize_name('for') == 'for_'
    assert regularize_name('__foo') == '__foo'
    assert regularize_name('as') == 'as_'
    assert regularize_name('_lambda') == '_lambda'
    assert regularize_name('$schema') == 'schema'
    assert regularize_name('__7abc') == '__7abc'
    assert regularize_name('Foo<(string)>') == 'Foo_string'

    duplicates = ['for_', 'for_1']
    assert regularize_name('for', duplicates) == 'for_2'
    assert regularize_name('for_', duplicates) == 'for_2'
    assert regularize_name('for_1', duplicates) == 'for_2'


def test_trait_name_map():
    names = ['for', 'for_', '$for', '$schema', '$$FOO', 'bar', '_abc1']
    mapping = {'for_1': 'for',
               'for_2': '$for',
               'schema': '$schema',
               'FOO': '$$FOO'}
    assert trait_name_map(names) == mapping


def test_sorted_repr():
    D = {'A': 4, 'B': 5}
    reprD = sorted_repr(D)
    assert reprD == "{'A': 4, 'B': 5}"
    assert eval(reprD) == D

    D = {'1': 4, 2: 5}
    reprD = sorted_repr(D)
    assert reprD in ["{'1': 4, 2: 5}", "{2: 5, '1': 4}"]
    assert eval(reprD) == D

    D = {'B': {'y': 4, 'x':3}, 'A': 5}
    reprD = sorted_repr(D)
    assert reprD == "{'A': 5, 'B': {'x': 3, 'y': 4}}"
    assert eval(reprD) == D
