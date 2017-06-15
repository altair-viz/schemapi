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

simple_object = {
    'schema': {
        "type": "object",
        "properties": {
            "foo": {"type": "string"},
            "bar": {"type": "number"},
            "baz": {"type": "boolean"}
        }
    },
    'valid': [
        {
            "foo": "hello world",
            "bar": 3.141592653,
            "baz": True
        },
        {
            "foo": "a string",
            "bar": 42,
            "baz": False
        },
    ],
    'invalid': [
        {
            "foo": "hello",
            "bar": "world",
            "baz": True
        },
        {
            "foo": 42,
            "bar": 43,
            "baz": False
        },
        {
            "foo": "a string",
            "bar": 42,
            "baz": "True"
        }
    ]
}
