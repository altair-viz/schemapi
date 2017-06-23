import os
from altair_parser import JSONSchema
from altair_parser.utils.save_module import save_module

module = '_altair_schema'
if os.path.exists(module):
    raise ValueError("{module} already exists.".format(module=module))

schemafile = 'altair_parser/schemas/vega-lite-v2.0.0.json'
schema = JSONSchema.from_json_file(schemafile, module='_altair_schema')
source_tree = schema.source_tree()
print("writing to {module}".format(module=module))
save_module(source_tree, module, os.path.abspath('.'))

# def find_anonymous_objects(schema, name='#'):
#     for prop, subschema in schema.get('definitions', {}).items():
#         prop = name + '/definitions/' + prop
#         find_anonymous_objects(subschema, prop)
#
#     for subschema in schema.get('anyOf', []):
#         prop = name + '/anyOf'
#         find_anonymous_objects(subschema, prop)
#
#     for prop, subschema in schema.get('properties', {}).items():
#         prop = name + '/' + prop
#         if subschema.get('type', None) == 'object':
#             print()
#             print(prop)
#             pprint.pprint(subschema)
#         find_anonymous_objects(subschema, name=prop)
#
# find_anonymous_objects(schema.schema)
