from functools import wraps
from .utils import load_from_str_or_buf
import json as json_
from os import makedirs
from os.path import dirname

@wraps(json_.load)
def load(path_or_buf, **kwargs):
    return json_.load(fp=load_from_str_or_buf(path_or_buf), **kwargs)

@wraps(json_.dump)
def dump(obj, path_or_buf, **kwargs):
    if isinstance(path_or_buf, str):
        makedirs(dirname(path_or_buf), exist_ok=True)
        with open(path_or_buf, 'w', encoding='utf-8') as fp:
            return dump(obj, path_or_buf=fp, **kwargs)
    
    return json_.dump(obj=obj, fp=path_or_buf, **kwargs)

def __getattr__(x):
    return getattr(json_, x)

import pandas as pd

def generate_json_schema(data):
    def infer_schema(value):
        if isinstance(value, dict):
            properties = {}
            required = []
            for k, v in value.items():
                properties[k] = infer_schema(v)
                required.append(k)
            return {
                "type": "object",
                "properties": properties,
                "required": required
            }
        elif isinstance(value, list):
            if value:
                item_schemas = [infer_schema(item) for item in value]
                # Simplify if all item schemas are the same
                if all(schema == item_schemas[0] for schema in item_schemas):
                    return {
                        "type": "array",
                        "items": item_schemas[0]
                    }
                else:
                    return {
                        "type": "array",
                        "items": {
                            "anyOf": item_schemas
                        }
                    }
            else:
                # Empty array; cannot determine item schema
                return {
                    "type": "array",
                    "items": {}
                }
        else:
            # Primitive types
            if isinstance(value, str):
                return {"type": "string"}
            elif isinstance(value, bool):
                return {"type": "boolean"}
            elif isinstance(value, int):
                return {"type": "integer"}
            elif isinstance(value, float):
                return {"type": "number"}
            elif value is None:
                return {"type": "null"}
            else:
                return {}

    return infer_schema(data)

def json_to_table(json_schema, json_data):
    def flatten_json(data, schema, parent_key='', parent_rows=None):
        if parent_rows is None:
            parent_rows = [{}]

        data_type = schema.get('type')

        if data_type == 'object':
            properties = schema.get('properties', {})
            for key, subschema in properties.items():
                value = data.get(key)
                new_key = f"{parent_key}.{key}" if parent_key else key

                new_parent_rows = []
                for parent_row in parent_rows:
                    if value is not None:
                        sub_rows = flatten_json(value, subschema, new_key, [parent_row.copy()])
                        new_parent_rows.extend(sub_rows)
                    else:
                        parent_row[new_key] = None
                        new_parent_rows.append(parent_row)
                parent_rows = new_parent_rows

        elif data_type == 'array':
            items_schema = schema.get('items')
            new_parent_rows = []
            if isinstance(data, list):
                for item in data:
                    for parent_row in parent_rows:
                        sub_rows = flatten_json(item, items_schema, parent_key, [parent_row.copy()])
                        new_parent_rows.extend(sub_rows)
                parent_rows = new_parent_rows
            else:
                # Data is not a list but schema says it should be
                pass  # Handle error or treat as empty list
        else:
            # Primitive type
            for parent_row in parent_rows:
                parent_row[parent_key] = data

        return parent_rows

    rows = flatten_json(json_data, json_schema)
    df = pd.DataFrame(rows)
    return df