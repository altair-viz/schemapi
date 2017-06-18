"""
JSONSchema test cases.

Each object defined in this file should be a dictionary with three keys:

- 'schema' should be to a dictionary defining a valid JSON schema.
- 'valid' should be a list of dictionaries, each of which is a valid
  instance under the specified schema.
- 'invalid' should be a list of dictionaries, each of which is an invalid
  instance under the specified schema.

These test cases are used by test_testcases.py
"""

simple_types = {
    'schema': {
        "type": "object",
        "properties": {
            "str": {"type": "string"},
            "num": {"type": "number"},
            "int": {"type": "integer"},
            "bool": {"type": "boolean"},
            "null": {"type": "null"}
        }
    },
    'valid': [
        {
            "str": "hello world",
            "num": 3.141592653,
            "int": 42,
            "bool": True,
            "null": None
        }
    ],
    'invalid': [
        {
            "str": 100,
            "num": 3.141592653,
            "int": 42,
            "bool": True,
            "null": None
        },
        {
            "str": "hello world",
            "num": "3.14",
            "int": 42,
            "bool": True,
            "null": None
        },
        {
            "str": "hello world",
            "num": 3.141592653,
            "int": 4.2,
            "bool": True,
            "null": None
        },
        {
            "str": "hello world",
            "num": 3.141592653,
            "int": 42,
            "bool": "True",
            "null": None
        },
        {
            "str": "hello world",
            "num": 3.141592653,
            "int": 42,
            "bool": "True",
            "null": 123
        },
    ]
}

compound_types = {
    'schema': {
        "type": "object",
        "properties": {
            "str_or_num": {"type": ["string", "number"]},
            "num_or_null": {"type": ["number", "null"]}
        }
    },
    'valid': [
        {
            "str_or_num": 42,
            "num_or_null": None
        },
        {
            "str_or_num": "42",
            "num_or_null": 42
        }
    ],
    'invalid': [
        {
            "str_or_num": [1, 2, 3],
            "num_or_null": None
        },
        {
            "str_or_num": None,
            "num_or_null": 42
        },
        {
            "str_or_num": 50,
            "num_or_null": "hello"
        }
    ]
}

array_types = {
    'schema': {
        'properties': {
            'intarray': {
                'type': 'array',
                'items': {'type': 'integer'}
            },
            'strnullarray': {
                'type': 'array',
                'items': {'type': ['string', 'null']}
            }
        }
    },
    'valid': [
        {
            'intarray': [1, 2, 3],
            'strnullarray': ["hello", "there", None]
        }
    ],
    'invalid': [
        {
            'intarray': [1, 2, 3.14],
            'strnullarray': ["hello", "there", None]
        },
        {
            'intarray': [1, 2, 3],
            'strnullarray': [42, "str", None]
        }
    ],
}

enum_types = {
    'schema': {
        'properties': {
            'intenum': {
                'enum': [1, 2, 3]
            },
            'strenum': {
                'enum': ['a', 'b', 'c']
            },
            'mixedenum': {
                'enum': [1, 'A', False, None],
            }
        }
    },
    'valid': [
        {
            'intenum': 3,
            'strenum': 'b',
            'mixedenum': 'A'
        },
        {
            'intenum': 2,
            'strenum': 'a',
            'mixedenum': False
        },
        {
            'intenum': 1,
            'strenum': 'c',
            'mixedenum': None
        }
    ],
    'invalid': [
        {
            'intenum': '3',
            'strenum': 'b',
            'mixedenum': 'A'
        },
        {
            'intenum': 2,
            'strenum': 'a',
            'mixedenum': 'False'
        },
        {
            'intenum': 1,
            'strenum': 3.14,
            'mixedenum': None
        }
    ]
}
