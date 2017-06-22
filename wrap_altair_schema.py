import os
from altair_parser import JSONSchema
from altair_parser.utils.save_module import save_module

schema = JSONSchema.from_json_file('altair_parser/schemas/vega-lite-v2.0.0.json')

source_tree = schema.source_tree()

print("writing to ./altair_schema/")
save_module(source_tree, 'altair_schema', os.path.abspath('.'))

print(schema.anonymous_objects)

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
