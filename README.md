# schemapi

Auto-generate Python APIs from JSON schema specifications

[![build status](http://img.shields.io/travis/altair-viz/schemapi/master.svg?style=flat)](https://travis-ci.org/altair-viz/schemapi)

## About

[JSON Schema](http://json-schema.org/) is a vocabulary that allows you to
annotate and validate JSON documents.

``schemapi`` is a package that lets you auto-generate simple Python object-based
APIs given a valid JSON schema specification.
The generated code is essentially a 
[traitlets](http://traitlets.readthedocs.io/)-based
Python object hierarchy designed to allow validated JSON documents to be
created with Python code.

The motivating case for this package was the [Altair](http://altair-viz.github.io)
visualization library: Altair is a Python API built on the
[Vega-Lite](https://vega.github.io/vega-lite/) grammar of visualization,
and the bulk of the Altair package is generated automatically using ``schemapi``.

## Simple Example

As a very simple example, imagine you have the following simple JSON schema,
defined as a Python dictionary:

```python
>>> schema = {
...   'properties': {
...     'name': {'type': 'string'},
...     'age': {'type': 'integer'}
...   }
... }
```

This schema specifies that a data instance is valid if it has a key "name" that
maps to a string, and a key "age" that maps to an integer.
So, for example, this dictionary would be valid:

```python
>>> valid = {'name': 'suzie', 'age': 32}
```

while this dictionary would not:

```python
>>> invalid = {'name': 'suzie', 'age': 'old'}
```


### Validation with ``jsonschema``


In Python, you can use the ``jsonschema`` package to validate any data objects against this schema. For example, this data passes:

```python
>>> jsonschema.validate(valid, schema)
```

While this data fails, as indicated by the ``ValidationError``:

```python
>>> jsonschema.validate(invalid, schema)
ValidationError: 'old' is not of type 'integer'
```

### API Generation

The ``schemapi`` package lets you generate a Python API that allows you to build
up this kind of data not with raw dictionaries, but with an object-oriented
Python approach.

For example, here is how you can create a local module named ``myschema`` that
includes an object hierarchy designed for creating and validating data under
this schema:

```python
>>> import schemapi

>>> api = schemapi.JSONSchema(schema)

>>> api.write_module('myschema')
saving to myschema at /Users/jakevdp/github/altair-viz/schemapi
```

The result of this is that a new Python module named ``myschema`` is written
to disk in the local directory; we can import the root object (an object of
type derived from [traitlets.HasTraits](http://traitlets.readthedocs.io/en/stable/using_traitlets.html)),
and use it to construct some data:

```python
>>> from myschema import Root

>>> data = Root(name='suzie', age=32)
```

This data can be output in the form of a JSON dict:

```python
>>> data.to_dict()
{'age': 32, 'name': 'suzie'}
```

The object can also be instantiated from a dict:

```python
data = Root.from_dict({'age': 32, 'name': 'suzie'})
```

The object allows data to be modified in-place using attribute access:

```python
>>> data.name = 'frank'

>>> data.to_dict()
{'age': 32, 'name': 'frank'}
```

And any time the data is set, it is validated to make sure it is compatible with
the schema definition, raising a ``traitlets.TraitError`` if the value is not
compatible:

```python
>>> data.age = 'old'
TraitError: The 'age' trait of a Root instance must be a JSON integer, but a value of 'old' <class 'str'> was specified.

>>> Root(name='suzie', age='old')
TraitError: The 'age' trait of a Root instance must be a JSON integer, but a value of 'old' <class 'str'> was specified.
```

By utilizing JSONSchema
[definitions and references](https://cswr.github.io/JsonSchema/spec/definitions_references/), much more complicated nested object hierarchies
are possible, and the generated classes can be subclassed in order to create
domain-specific APIs for specifying data that can be serialized to and from
JSON. For an example of a much more complicated schema in action, see the 
[Altair](http://altair-viz.github.io) project.

## Installation

You can install the released version from [PyPI](http://pypi.python.org/pypi/schemapi) using ``pip``:

    $ pip install schemapi

To install the bleeding-edge version from source, you can download this
repository and installing locally:

    $ git clone https://github.com/altair-viz/schemapi.git
    $ cd schemapi
    $ pip install .

## Testing

To run the test suite you must have [py.test](http://pytest.org/latest/) installed.
To run the tests, use

```
py.test --pyargs schemapi
```
(you can omit the `--pyargs` flag if you are running the tests from a source checkout).


## License

``schemapi`` is released under a [3-Clause BSD License](LICENSE).


## Feedback and Contribution

We welcome any input, feedback, bug reports, and contributions via schemapi's
[GitHub repository](http://github.com/altair-viz/schemapi/).