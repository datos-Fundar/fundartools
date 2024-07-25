import io
import os
from operator import contains
from functools import reduce, partial
from typing import NewType, Callable, TypeVar, Protocol, Generic, Optional
from datetime import datetime

class classproperty(property):
    """Utilidad para crear propiedades de clase"""

    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()

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

# https://hackage.haskell.org/package/base-4.19.1.0/docs/Prelude.html#v:fst
fst = access(0)

# https://hackage.haskell.org/package/base-4.19.1.0/docs/Prelude.html#v:snd
snd = access(1)

def identity_single_argument(x):
    return x

def identity(*args):
    return args

def is_empty(x):
    return False if x else True

def _apply_to(f, i, x):
    return type(x)(f(y) if (j == i) else y for j,y in enumerate(x))

def apply_to(f, i):
    """
    Applies a function to the ith element of an indexable object.
    Leaves the rest just as is.
    """
    return lambda x: _apply_to(f, i, x)

# https://hackage.haskell.org/package/base-4.19.1.0/docs/Control-Arrow.html#v:first
first = partial(apply_to, i=0)

# https://hackage.haskell.org/package/base-4.19.1.0/docs/Control-Arrow.html#v:second
second = partial(apply_to, i=1)

A = TypeVar('A')
def group_by(predicate: Callable[[A, A], bool], elements: list[A]) -> list[list[A]]:
    if not elements:
        return []
    
    def go(groups, x):
        if not groups:
            return [[x]]
        
        last_group = groups[-1]
        if predicate(x, last_group[0]):
            groups[-1] = last_group + [x]
        else:
            groups.append([x])
        return groups

    groups = []
    for element in elements:
        groups = go(groups, element)
    return groups

def _flatten(lst, flat_list):
    for item in lst:
        if isinstance(item, list):
            _flatten(item, flat_list)
        else:
            flat_list.append(item)

    return flat_list

def flatten(nested_list):
    return _flatten(nested_list, [])


def groupby(predicate, elements):
    match_count = 0
    
    for x in elements:
        if predicate(x):
            match_count += 1
    
    left = [None for _ in range(match_count)]
    right = [None for _ in range(len(elements) - match_count)]

    i, j = 0, 0
    for x in elements:
        if predicate(x):
            left[i] = x
            i += 1
        else:
            right[j] = x
            j += 1
    
    return left, right
    
# =============================================================================================

class staticproperty(property):
    """Utilidad para crear propiedades estáticas (que no tomen el puntero a self)"""

    def __get__(self, cls, owner):
        return staticmethod(self.fget).__get__(None, owner)()

class SingletonMeta(type):
    """
    Fuente: github.com/datos-Fundar/fundartools
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
    
class Singleton(metaclass=SingletonMeta):
    def __init_subclass__(cls) -> None:
        cls.instance = classproperty(lambda _: cls.get_instance())
    
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

def load_from_str_or_buf(input_data) -> io.BytesIO:
    match input_data:
        case string if isinstance(input_data, str):
            if not os.path.exists(input_data):
                raise FileNotFoundError(f'File {string} not found.')
            if not os.path.isfile(string):
                raise ValueError("Input is a folder, not a file.")
            
            with open(string, 'rb') as file:
                return io.BytesIO(file.read())
            
        case buffer if isinstance(input_data, (io.BytesIO, io.StringIO)):
            return buffer
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

from inspect import signature

def argumentsOf(f): return len(signature(f).parameters)

def curry(f: callable):
    """
    Currifica una funcion de der. a izq.
    Por ejemplo:

    curry(lambda a,b: a/b) === lambda b: lambda a: a/be
    """
    def curried(*args):
        if len(args) == argumentsOf(f): return f(*args)
        else: return lambda x: curried(x, *args)
    return curried

# =============================================================================================

class Negate(object):
    def __matmul__(self, other):
        return lambda *args, **kwargs: not other(*args, **kwargs)

class negate(): ...
del negate

negate = Negate()

# =============================================================================================

def print_id(x):
    print(x)
    return x

# =============================================================================================

class now:
    # noinspection PyMethodParameters
    @staticproperty
    def string():
        return datetime.now().strftime('%d-%m-%y_%H%M%S')
    
    def format(fmt):
        return datetime.now().strftime(fmt)

# ============================================================================================

class MethodMapping(dict):
    """Diccionario que asocia claves a funciones. Sirve para crear selectores de estrategia."""

    def __register__(self, key, f):
        self[key] = f
        return f

    def register(self, key_or_alias):
        match key_or_alias:
            case alias if isinstance(key_or_alias, str):
                return lambda f: self.__register__(alias, f)
            case function if callable(key_or_alias):
                return self.__register__(function.__name__, function)
            
    def __getattr__(self, k):
        return self[k]

# ============================================================================================   

def throw(ex):
    raise ex

class Placeholder:    
    def __init_subclass__(cls) -> None:
        cls.__init__ = lambda *_, **__: throw(TypeError(f"'{cls.__name__}' is a placeholder and cannot be instantiated."))
        cls.__init_subclass__ = lambda *_, **__: throw(TypeError(f"'{cls.__name__}' is a placeholder and cannot be subtyped."))

# ============================================================================================

def search_downwards(name: str, start_path: str, max_depth: int, current_depth: int=0) -> Optional[str]:
    if current_depth > max_depth:
        return None
    
    for root, dirs, files in os.walk(start_path):
        if name in files or name in dirs:
            return os.path.join(root, name)
        
        if current_depth + 1 > max_depth:
            break
        
        for d in dirs:
            result = search_downwards(name, os.path.join(root, d), max_depth, current_depth + 1)
            if result:
                return result

    return None

def search_upwards(name: str, start_path: str, max_up_depth: int, max_down_depth: int, current_up_depth: int=0) -> Optional[str]:
    if current_up_depth > max_up_depth:
        return None
    
    result = search_downwards(name, start_path, max_down_depth)
    if result:
        return result
    
    parent_dir = os.path.abspath(os.path.join(start_path, '..'))
    
    if parent_dir == start_path:
        return None
    
    return search_upwards(name, parent_dir, max_up_depth, max_down_depth, current_up_depth + 1)

def find_file(name: str, path: str, max_up_depth: int=3, max_down_depth: int=3, throw_error: bool=False) -> Optional[str]:
    result = search_downwards(name, path, max_down_depth)

    if result:
        # get absolute path
        result = os.path.abspath(result)
        return result
    

    result = search_upwards(name, path, max_up_depth, max_down_depth)
    if result:
        # get absolute path
        result = os.path.abspath(result)
        return result
    
    if throw_error:
        raise FileNotFoundError(f"File '{name}' not found.")
    
def split_path_recursively(path: str) -> list:
    if path == os.path.sep:
        return []
    
    head, tail = os.path.split(path)
    
    if head == '' or head == path:
        return [tail]
    
    return split_path_recursively(head) + [tail]
