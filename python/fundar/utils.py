import io
import os
from operator import contains
from functools import reduce, partial
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

def access(i):
    return lambda x: x[i]

fst = access(0)
snd = access(1)

def _apply_to(f,i,x):
    if i == 0:
        return type(x)(f(x[0]), *x[1:])
    if i == len(x)-1:
        return type(x)((*x[:-1], f(x[-1])))
    else:
        return type(x)(*x[:i], f(x[i]), *x[i+1:])

def apply_to(f, i):
    """
    Applies a function to the ith element of an indexable object.
    Leaves the rest just as is.
    """
    return lambda x: _apply_to(f, i, x)

first = partial(apply_to, i=0)
second = partial(apply_to, i=1)
    
# =============================================================================================

class staticproperty(property):
    """Utilidad para crear propiedades estáticas (que no tomen el puntero a self)"""

    def __get__(self, cls, owner):
        return staticmethod(self.fget).__get__(None, owner)()

class Singleton(type):
    """
    Metaclase que implementa el patrón de singleton.
    Las clases que la heredan no pueden ser instanciadas más de una vez.
    Provee un método 'get_instance' que es heredado, el cual:
    - Si la clase no está instanciada, la crea.
    - Si está instanciada, la devuelve.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
            return instance

        raise RuntimeError("Class already instantiated. Use get_instance()")

    def get_instance(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
    
# =============================================================================================

_T_co = TypeVar('_T_co')
_T = TypeVar('_T')

class SupportsNext(Protocol[_T_co]):
    def __next__(self) -> _T_co: ...


class SupportsIter(Protocol[_T_co]):
    def __iter__(self) -> _T_co: ...

class Attribute(Generic[_T]): ...

class Final(Generic[_T]):
    """Indica que la variable no puede ser reasignada, pero si puede mutar."""


class Mutable(Generic[_T]):
    """Indica que la variable puede ser reasignada y mutar"""


class Inmutable(Generic[_T]):
    """Indica que la variable no puede ser reasignada ni mutar"""

def getattrc(attr: str):
    """Versión currificada de 'getattr'"""
    return lambda obj: getattr(obj, attr)

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

# =============================================================================================

from typing import Iterable, Union, Type, Dict

def text_wrap(s: str, max_length=100) -> str:
    if len(s) >= max_length:
        return s[:max_length]+'\n'+text_wrap(s[max_length:], max_length)
    return s

def is_subscrevable(x: object|type) -> bool: # Raises Exception^AttributeError
    if not isinstance(x, type):
        return is_subscrevable(type(x))
    try:
        x.__getitem__
        return True
    except Exception as e:
        match e:
            case AttributeError():
                return False
            case _:
                raise e

def internal_type_of_iterable(s: Iterable) -> type|Union[type]:
    missing_first = object()
    iterator = iter(s)
    first_element = next(iterator, missing_first)
    
    if first_element is missing_first:
        raise ValueError('Empty iterable')

    internal_type = type(first_element)
    for t in map(type, iterator):
        internal_type |= t

    return internal_type

def _typeof_iterable(s: Iterable) -> tuple[Type[Iterable], type|Union[type]]:
    base_type = type(s)
    internal_type = internal_type_of_iterable(s)
    
    if not is_subscrevable(base_type):
        print(base_type)
        return None
    return base_type, internal_type

def typeof_iterable(s: Iterable) -> Type[Type]:
    base_type, internal_type = _typeof_iterable(s)
    return base_type[internal_type]

def _typeof_dict(d: dict) -> tuple[Type[dict], type|Union[type]]:
    keys = internal_type_of_iterable(d.keys())
    values = internal_type_of_iterable(d.values())
    return keys, values

def typeof_dict(d: dict) -> Type[Dict[type|Union[type], type|Union[type]]]:
    keys, values = _typeof_dict(d)
    return dict[keys, values]

def isiterable(s: object) -> bool:
    try:
        iter(s)
        return True
    except TypeError:
        return False

def split(condition):
    def _split(xs):
        successful, failed = [], []
        for x in xs:
            (successful if condition(x) else failed).append(x)
        return successful, failed
    return _split

# =============================================================================================