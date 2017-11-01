"""Schemas for testing"""
__all__ = ['load_schema']

import os
import json


SCHEMA_DIR = os.path.join(os.path.dirname(__file__), 'json')


def load_schema(filename):
    with open(os.path.join(SCHEMA_DIR, filename)) as f:
        schema = json.load(f)
    return schema


def iter_schemas():
    for filename in os.listdir(SCHEMA_DIR):
        if filename.endswith('.json'):
            yield load_schema(filename)

def iter_schemas_with_names():
    for filename in os.listdir(SCHEMA_DIR):
        if filename.endswith('.json'):
            yield (filename, load_schema(filename))
