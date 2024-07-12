import pandas as pandas_
from pandas.core.series import Series as Series_
from copy import copy
from functools import partial, wraps
from typing import TypeAlias, NewType, Type
import csv as csv_

original_to_csv = copy(pandas_.DataFrame.to_csv)

class DataFrame(pandas_.DataFrame): pass
del DataFrame

class Series(Series_): pass
del Series

formato_fundar = {
    'encoding': 'utf-8',
    'sep': ',',
    'quoting': csv_.QUOTE_ALL,
    'quotechar': '"',
    'lineterminator': '\n',
    'decimal': '.',
    'index': False,
    'float_format': '%.5f'
}

@wraps(original_to_csv)
def to_csv_patch(self, path_or_buf, **kwargs):
    return original_to_csv(self, path_or_buf, **(formato_fundar|kwargs))

pandas_.DataFrame.to_csv = to_csv_patch
setattr(Series_, 'has', lambda self, x: self.map(lambda y: x in y))
setattr(Series_, 'has_safe', lambda self, x: self.map(lambda y: False if '__contains__' not in dir(y) else x in y))

def __getattr__(name):
    return getattr(pandas_, name)