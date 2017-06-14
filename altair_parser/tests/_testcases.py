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
