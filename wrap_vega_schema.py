"""
Wrap the vega schema and save to a source tree
"""
import os
from schemapi import JSONSchema
from schemapi.utils import save_module

schemafile = 'schemapi/schemas/vega-v3.0.0.json'
module = '_vega_schema'

if os.path.exists(module):
    raise ValueError("{module} already exists.".format(module=module))

schema = JSONSchema.from_file(schemafile, module=module,
                                   definition_tags=['refs', 'defs'])
source_tree = schema.source_tree()
print("writing to {module}".format(module=module))
save_module(source_tree, module, os.path.abspath('.'))
