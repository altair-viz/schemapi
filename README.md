# schemapi

Auto-generate Python APIs from JSON schema specifications

[![build status](http://img.shields.io/travis/altair-viz/schemapi/master.svg?style=flat)](https://travis-ci.org/altair-viz/schemapi)

## About

[JSON Schema](http://json-schema.org/) is a vocabulary that allows you to
annotate and validate JSON documents, and this kind of validation can be
performed using the [jsonschema](https://pypi.python.org/pypi/jsonschema)
Python package.

``schemapi`` is a package with a slightly different aim: given a JSON schema
specification, ``schemapi`` can generate a
[traitlets](http://traitlets.readthedocs.io/)-based
Python object hierarchy designed to allow validated JSON documents to be
created with Python code.

The motivating case for this package was the [Altair](http://altair-viz.github.io)
visualization library: Altair is a Python API built on the
[Vega-Lite](https://vega.github.io/vega-lite/) grammar of visualization,
and the bulk of the Altair package is generated automatically using ``schemapi``.

## Simple Example

As a very simple example, imagine you have the following simple schema,
defined as a Python dictionary:

```python
>>> schema = {
...   'properties': {
...     'name': {'type': 'string'},
...     'age': {'type': 'integer'}
...   }
... }
```

### Validation with ``jsonschema``

You can use the ``jsonschema`` package to validate any data objects against this schema. For example, this data passes:

```python
>>> data = {'name': 'suzie', 'age': 32}
>>> jsonschema.validate(data, schema)
```

While this data fails:

```python
>>> data = {'name': 'suzie', 'age': 'old'}
>>> jsonschema.validate(data, schema)
---------------------------------------------------------------------------
ValidationError                           Traceback (most recent call last)
<ipython-input-18-9b2b505e753e> in <module>()
----> 1 jsonschema.validate(data, schema)

/Users/jakevdp/anaconda/envs/altair-dev-3.5/lib/python3.5/site-packages/jsonschema/validators.py in validate(instance, schema, cls, *args, **kwargs)
    476         cls = validator_for(schema)
    477     cls.check_schema(schema)
--> 478     cls(schema, *args, **kwargs).validate(instance)

/Users/jakevdp/anaconda/envs/altair-dev-3.5/lib/python3.5/site-packages/jsonschema/validators.py in validate(self, *args, **kwargs)
    121         def validate(self, *args, **kwargs):
    122             for error in self.iter_errors(*args, **kwargs):
--> 123                 raise error
    124
    125         def is_type(self, instance, type):

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

By utilizing JSONSchema definitions, much more complicated object hierarchies
are possible, and the generated classes can be subclassed in order to create
domain-specific APIs for specifying data that can be serialized to and from JSON.

## Installation

You can install the released version from [PyPI](http://pypi.python.org/pypi/schemapi) using ``pip``:

    $ pip install schemapi

To install the bleeding-edge version from source, you can download this
repository and installing locally:

    $ git clone https://github.com/altair-viz/schemapi.git
    $ cd schemapi
    $ pip install .
