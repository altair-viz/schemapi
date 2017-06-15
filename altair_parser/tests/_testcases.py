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
            "bool": {"type": "boolean"}
        }
    },
    'valid': [
        {
            "str": "hello world",
            "num": 3.141592653,
            "int": 42,
            "bool": True
        }
    ],
    'invalid': [
        {
            "str": 100,
            "num": 3.141592653,
            "int": 42,
            "bool": True
        },
        {
            "str": "hello world",
            "num": "3.14",
            "int": 42,
            "bool": True
        },
        {
            "str": "hello world",
            "num": 3.141592653,
            "int": 42.57,
            "bool": True
        },
        {
            "str": "hello world",
            "num": 3.141592653,
            "int": 42,
            "bool": "True"
        },
    ]
}

compound_types = {
    'schema': {
        "type": "object",
        "properties": {
            "str_or_num": {"type": ["string", "number"]}
        }
    },
    'valid': [
        {"str_or_num": 42},
        {"str_or_num": "42"}
    ],
    'invalid': [
        {"str_or_num": [1, 2, 3]}, 
        {"str_or_num": None}
    ]
}
