"""
Wrap the vega-lite schema and save to a source tree
"""
import os
from schemapi import JSONSchema
from schemapi.utils import save_module

schemafile = 'schemapi/schemas/vega-lite-v2.0.0.json'
module = '_vegalite_schema'

if os.path.exists(module):
    raise ValueError("{module} already exists.".format(module=module))

schema = JSONSchema.from_file(schemafile, module=module)
source_tree = schema.source_tree()
print("writing to {module}".format(module=module))
save_module(source_tree, module, os.path.abspath('.'))
