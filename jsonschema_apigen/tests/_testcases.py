"""
JSONSchema test cases.

Each object defined in this file should be a dictionary with three keys:

- 'schema' should be a dictionary defining a valid JSON schema.
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
                'enum': [1, 2, 3],
                'type': 'integer'
            },
            'strenum': {
                'enum': ['a', 'b', 'c'],
                'type': 'string'
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

simple_references = {
    'schema': {
        'properties': {
            'a': {
                '$ref': '#/definitions/StringOrInt'
            },
            'b': {
                '$ref': '#/definitions/CompoundObject'
            }
        },
        'definitions': {
            'StringOrInt': {
                'type' : ['string', 'integer']
            },
            'CompoundObject': {
                'type': 'object',
                'properties': {
                    'val': {'type': 'integer'},
                    'name': {'type': 'string'}
                }
            }
        }
    },
    'valid': [{
        'a': 'hello',
        'b': {'name': 'jake', 'val': 100}
    },
    {
        'a': 42,
        'b': {'name': 'douglas', 'val': 42}
    }],
    'invalid': [{
        'a': None,
        'b': {'name': 'douglas', 'val': 'something else'}
    },
    {
        'a': 3.14159,
        'b': {'name': 'douglas', 'val': 42}
    }]
}

simple_anyof = {
    'schema': {
        'properties': {
            'value': {
                'anyOf': [
                    {'type': 'integer'},
                    {'type': 'array', 'items': {'type': 'integer'}}
                ]
            }
        }
    },
    'valid': [
        {'value': 4},
        {'value': [2, 3, 4]}
    ],
    'invalid': [
        {'value': 'a'},
        {'value': [1, 2, 'a']}
    ]
}

simple_oneOf = {
    'schema': {
        'properties': {
            'value': {
                'oneOf': [
                    {'type': 'integer'},
                    {'enum': [1, 2, 1.5, 'a']}
                ]
            }
        }
    },
    'valid': [
        {'value': 4},
        {'value': 1.5},
        {'value': 'a'}
    ],
    'invalid': [
        {'value': 1},
        {'value': 2}
    ]
}

simple_allOf = {
    'schema': {
        'properties': {
            'value': {
                'allOf': [
                    {'type': 'integer'},
                    {'enum': [1, 2, 1.5, 'a']}
                ]
            }
        }
    },
    'valid': [
        {'value': 1},
        {'value': 2}
    ],
    'invalid': [
        {'value': 4},
        {'value': 1.5},
        {'value': 'a'}
    ]
}

simple_not = {
    'schema': {
        'properties': {
            'value': {
                'not': {'type': 'integer'},
            }
        }
    },
    'valid': [
        {'value': [1, 2, 3]},
        {'value': 'a'},
        {'value': None}
    ],
    'invalid': [
        {'value': 0},
        {'value': 1},
        {'value': 2}
    ]
}

passthrough_ref = {
    'schema': {
        '$ref' : '#/definitions/TopLevel',
        'definitions': {
            'TopLevel': {
                'properties': {
                    'val': {'type': 'integer'},
                    'name': {'type': 'string'}
                }
            }
        }
    },
    'valid': [
        {'val': 42, 'name': 'the_answer'}
    ],
    'invalid': [
        {'val': 'yo', 'name': 123}
    ]
}

anonymous_objects = {
    'schema': {
        'type': 'object',
        'properties': {
            'item': {
                'type': 'object',
                'properties': {
                    'val': {'type': 'integer'},
                    'name': {'type': 'string'}
                }
            }
        }
    },
    'valid': [
        {'item': {'val': 42, 'name': "the_answer"}}
    ],
    'invalid': [
        {'item': {'val': "42", 'name': 100}},
        {'item': 42}
    ]
}


circular_reference = {
    'schema': {
        '$ref': '#/definitions/Repeat',
        'definitions': {
            'Repeat': {
                'type': 'object',
                'properties': {
                    'repeat': {
                        'anyOf': [
                            {'$ref': '#/definitions/Repeat'},
                            {'type': 'string'}
                        ]
                    }
                }
            }
        }
    },
    'valid': [
        {'repeat': 'foo'},
        {'repeat': {'repeat': 'foo'}},
        #{'repeat': {'repeat': {'repeat': 'foo'}}},
    ],
    'invalid': []
}

root_reference = {
    'schema': {
        'properties': {
            'val': {'type': 'string'},
            'foo': {'$ref': '#'}
        }
    },
    'valid': [
        {'val': 'first'},
        {'val': 'first',
         'foo': {'val': 'second'}},
        {'val': 'first',
         'foo': {'val': 'second',
                 'foo': {'val': 'third'}}}
    ],
    'invalid': [
        {'foo': {'val': 42}}
    ]
}

additionalProperties_test = {
    'schema': {
        'type': 'object',
        'properties': {
            'foo': {'type': 'integer'}
        },
        'additionalProperties': {
            'type': 'string'
        }
    },
    'valid': [
        {'foo': 42, 'name': 'blah'},
    ],
    'invalid': [
        {'foo': 42, 'value': 4},
        {'foo': 'blah'}
    ]
}

anyofobject_test = {
    'schema': {
        'anyOf': [
            {'$ref': '#/definitions/Foo1'},
            {'$ref': '#/definitions/Foo2'}
        ],
        'definitions': {
            'Foo1': {
                'properties': {
                    'val': {'type': 'integer'}
                }
            },
            'Foo2': {
                'properties': {
                    'val': {'type':'string'}
                }
            }
        }
    },
    'valid': [
        {'val': 42},
        {'val': 'blah'}
    ],
    'invalid': [
        {'val': None}
    ]
}

oneofobject_test = {
    'schema': {
        'oneOf': [
            {'$ref': '#/definitions/Foo1'},
            {'$ref': '#/definitions/Foo2'}
        ],
        'definitions': {
            'Foo1': {
                'properties': {
                    'val': {'type': 'integer'}
                }
            },
            'Foo2': {
                'properties': {
                    'val': {'type':'string'}
                }
            }
        }
    },
    'valid': [
        {'val': 42},
        {'val': 'blah'}
    ],
    'invalid': [
        {'val': None}
    ]
}


allofobject_test = {
    'schema': {
        'allOf': [
            {'$ref': '#/definitions/Foo1'},
            {'$ref': '#/definitions/Foo2'}
        ],
        'definitions': {
            'Foo1': {
                'properties': {
                    'score': {'type': 'integer'},
                }
            },
            'Foo2': {
                'properties': {
                    'name': {'type':'string'}
                }
            }
        }
    },
    'valid': [
        {'score': 42, 'name': 'hello'},
    ],
    'invalid': [
        {'score': 'blah'},
        {'name': 100}
    ]
}


enum_refs = {
    'schema': {
        'definitions': {
            'Mark': {
                "enum": ["point", "circle", "line"],
                "type": "string"
            },
            'MarkAlias': {
                '$ref': '#/definitions/Mark'
            },
            'MarkAliasAlias': {
                '$ref': '#/definitions/MarkAlias'
            },
            'TopLevel': {
                "properties": {
                    "mark1": {"$ref": "#/definitions/Mark"},
                    "mark2": {"$ref": "#/definitions/MarkAlias"},
                    "mark3": {"$ref": "#/definitions/MarkAliasAlias"},
                    "mark4": {"enum": ["box-plot", "error-bar"]},
                }
            }
        },
        "$ref": "#/definitions/TopLevel"
    },
    "valid": [
        {"mark1": "circle", "mark2": "line",
         "mark3": "point", "mark4": "box-plot"}
    ],
    "invalid": [
        {"mark1": "bad", "mark2": "line",
         "mark3": "point", "mark4": "box-plot"},
        {"mark1": "circle", "mark2": "bad",
         "mark3": "point", "mark4": "box-plot"},
        {"mark1": "circle", "mark2": "line",
         "mark3": "bad", "mark4": "box-plot"},
        {"mark1": "circle", "mark2": "line",
         "mark3": "point", "mark4": "bad"}
    ]
}
