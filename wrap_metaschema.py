"""
Wrap the draft-4 metaschema and save the source tree
"""
import os

from jsonschema._utils import load_schema
from schemapi import JSONSchema
from schemapi.utils import save_module

schema = load_schema('draft4')
module = '_metaschema'

if os.path.exists(module):
    raise ValueError("{module} already exists.".format(module=module))

schema = JSONSchema(schema, module=module)
source_tree = schema.source_tree()
print("writing to {module}".format(module=module))
save_module(source_tree, module, os.path.abspath('.'))
