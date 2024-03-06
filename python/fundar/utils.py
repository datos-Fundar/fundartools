import io
import os
from operator import contains
from functools import reduce
from typing import NewType, Callable, TypeVar, Protocol, Generic

# =============================================================================================

T = TypeVar('T')

class Indexable(Protocol[T]):
    def __getitem__(self, index: int) -> T: ...

class number(object): ...
number = int|float

# =============================================================================================

def compose2(f, g):
    return lambda *args, **kwargs: f(g(*args, **kwargs))

def compose(*fs):
    return reduce(compose2, fs)

def has(x):
    """Curried version of operator.contains"""
    return lambda y: contains(y, x)

def xmax(**kwargs):
    """
    Curried version of max.
    """
    return lambda x: max(x, **kwargs)

def call(f, *args, **kwargs):
    return f(*args, **kwargs)

def callx(*args, **kwargs):
    return lambda f: call(f, *args, **kwargs)

# =============================================================================================

Integer = TypeVar('Integer', int, int)
Float = TypeVar('Float', float, float)
Number = TypeVar('Number', int, float)

class Range(tuple[Number, Number], Generic[Number]): ...

class Max(tuple[T, ...]): ...
class Min(tuple[T, ...]): ...

class FloatRange(Range[float]): ...
class IntRange(Range[int]): ...

class UnboundedFloat(float): ...

class BoundedFloat(tuple[Float, Float]): ...
class BoundedInt(tuple[Integer, Integer]): ...

class Mapper(Callable[[Range], Callable[[Range, UnboundedFloat], BoundedFloat]]): ...

def mapper(ostart, ostop) -> Mapper:
    return lambda value, istart, istop: map_value(value, istart, istop, ostart, ostop)

def map_value(value, istart, istop, ostart, ostop):
    return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))

# =============================================================================================

def load_from_str_or_buf(input_data):
    match input_data:
        case string if isinstance(input_data, str):
            if not os.path.exists(input_data):
                raise FileNotFoundError(f'File {string} not found.')
            if not os.path.isfile(string):
                raise ValueError("Input is a folder, not a file.")
            
            with open(string, 'rb') as file:
                return io.BytesIO(file.read())
            
        case isinstance(input_data, (io.BytesIO, io.StringIO)):
            return input_data
        case _:
            raise TypeError("Unsupported input type. Please provide a valid file path or buffer.")
        
# =============================================================================================

def apply(f):
    """
    ...args :: tuple[varargs, varkwargs]
    y :: f(..args): Any
    f -> ...args -> y | tuple[...args, y]
    """
    def apply_to(*args, **kwargs):
        n = len(args)
        m = len(kwargs)
        if n+m == 0:
            return f()
        
        if n+m == n:
            if n == 1:
                x = args[0]
                return (x, f(x))
            else:
                return (args, f(*args))
        
        if n+m == m:
            return (kwargs, f(**kwargs))
        
        return (args, kwargs, f(*args, **kwargs))
    return apply_to