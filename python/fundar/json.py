from functools import wraps
from .utils import load_from_str_or_buf
import json as json_

@wraps(json_.load)
def load(path_or_buf, **kwargs):
    return json_.load(fp=load_from_str_or_buf(path_or_buf), **kwargs)

@wraps(json_.dump)
def dump(obj, path_or_buf, **kwargs):
    if isinstance(path_or_buf, str):
        with open(path_or_buf, 'w', encoding='utf-8') as fp:
            return dump(obj, path_or_buf=fp, **kwargs)
    
    return json_.dump(obj=obj, fp=path_or_buf, **kwargs)

def __getattr__(x):
    return getattr(json_, x)