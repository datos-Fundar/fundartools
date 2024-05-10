from collections.abc import Iterator
from .utils import callx, flatten
from functools import reduce, wraps
from operator import eq as equals, add

class List(list):
    """
    Subclase del primitivo 'list', con métodos adicionales para una manipulación de listas más funcional.
    En particular, convierte algunas operaciones lazy (map, filter, reduce) y las hace eager.
    """

    class _size(int):
        def __call__(self):
            return int(self)

    def map(*args):
        """
        Versión eager de map.
        """
        n = len(args)

        if n not in (1,2):
            raise ValueError(f'Expected 1 or 2 arguments, got {n}.')

        if n == 2:
            self, f = args
            return List(map(f, self))
        
        if n == 1:
            f = args[0]
            return lambda xs: List.map(xs, f)

    def filter(self, f):
        """
        Versión eager de filter.
        """
        return List(filter(f, self))
    
    def reduce(self, f, initial=None):
        """
        Versión eager de reduce.
        """
        if not initial:
            result = reduce(f, self)
        else:
            result = reduce(f, self, initial)

        if type(result) == list:
            return List(result)
        return result
    
    def safe_index(self, x, default=-1):
        """
        Devuelve el índice de x si está en la lista, o -1 en caso contrario.
        """
        try:
            return self.index(x)
        except ValueError:
            return default
    
    def zip(self, *args):
        """
        Versión eager de zip.
        """
        return List(zip(self, *args))
    
    def zipmap(self, *fs, keep=True):
        if keep:
            return List( self.zip(*(self.map(f) for f in fs)) )
        else:
            return List( zip(*(self.map(f) for f in fs)) )
    
    def find(self, f, not_found=None):
        """
        Devuelve x tal que f(x) == True, si existe, o una lista vacía en caso contrario.
        """
        matches = self.filter(f)
        return matches[0] if matches else not_found
    
    def indexof(self, f):
        """
        Devuelve el índice de la primera ocurrencia de x tal que f(x) == True, si existe, o -1 en caso contrario.
        Para obtener el índice de un objeto particular, usar list.index.
        """
        return self.index(self.find(f))
    
    def apply(self, *args, **kwargs):
        """
        Lista como functor aplicativo. (<*>)
        Sea L una lista de funciones [f1, f2, ..., fn] y x un valor, luego L.apply(x) es equivalente a [f1(x), f2(x), ..., fn(x)].
        """
        try:
            return self.map(callx(*args, **kwargs))
        
        except TypeError as e:
            if 'not callable' not in str(e):
                raise e
            
            non_callables = self.map(lambda x: getattr(x, '__call__', None) is not None).map({True: 0, False: 1}.__getitem__).reduce(add)
            error_str = 'There '
            error_str += 'is' if non_callables == 1 else 'are'
            error_str += f' {non_callables} non-callable element'
            error_str += 's' if non_callables > 1 else ''
            error_str += ' in the list.'
            raise TypeError(error_str)
        
    def unique(self, comparator=equals):
        """
        Devuelve una lista con los elementos únicos de la lista original.
        """
        #
        return List(set(self))
    
    def nunique(self):
        """
        Devuelve el número de elementos únicos en la lista.
        """
        return len(self.unique())
    
    def flatten(self):
        return List(flatten(self))
    
    @wraps(list.sort)
    def sort(self, **kwargs):
        self = List(sorted(self, **kwargs))
        return self
    
    def __getitem__(self, index):
        if isinstance(index, slice):
            return List(super().__getitem__(index))
        return super().__getitem__(index)
    
    @property
    def size(self):
        return List._size(len(self))

class DictKeys(List):
    def __call__(self):
        return self

class DictValues(List):
    def __call__(self):
        return self
    
class DictItems(tuple):
    def __call__(self):
        return self

class Dict(dict):

    @staticmethod
    def pass_values(f):
        return lambda _,v: f(v)
    
    @staticmethod
    def pass_keys(f):
        return lambda k,_: f(k)

    def filter(self, f, over=None):
        """
        Versión eager de filter.
        """
        if over is None:
            over = 'items'
        
        match over:
            case 'keys':
                return self.filter_keys(f)
            case 'values':
                return self.filter_values(f)
            case 'items':
                return Dict({k: v for k, v in super().items() if f(k, v)})
            case _:
                raise ValueError('Invalid value for "by", must be one of "keys", "values" or "items"')

    def filter_keys(self, f):
        """
        Versión eager de filter para las claves del diccionario.
        """
        return Dict({k: v for k, v in super().items() if f(k, v)})
    
    def filter_values(self, f):
        """
        Versión eager de filter para los valores del diccionario.
        """
        return Dict({k: v for k, v in super().items() if f(k, v)})
    
    def map(self, f, over=None):
        """
        Versión eager de map.
        """

        if over is None:
            over = 'items'
            
        match over:
            case 'keys':
                return self.map_keys(f)
            case 'values':
                return self.map_values(f)
            case 'items':
                return List(super().items()).map(lambda x: f(*x))
            case _:
                raise ValueError('Invalid value for "by", must be one of "keys", "values" or "items"')
    
    def map_values(self, f):
        """
        Versión eager de map para los valores del diccionario.
        """
        return Dict({k: f(k,v) for k, v in super().items()})
    
    def map_keys(self, f):
        """
        Versión eager de map para las claves del diccionario.
        """
        return Dict({f(k,v): v for k, v in super().items()})
    
    @property
    def keys(self):
        return DictKeys(super().keys())
    
    @property
    def values(self):
        return DictValues(super().values())
    
    @property
    def items(self):
        return DictItems(x for x in super().items())
    
    def __iter__(self) -> Iterator:
        return iter(self.items)
    

class bijection:
    @classmethod
    def from_list(cls, xs):
        if isinstance(xs, list):
            if all(map(lambda x: isinstance(x, tuple) and len(x) == 2, xs)):
                return cls(dict(xs))
            raise TypeError
        raise TypeError
                
    def __init__(self, d: None|dict = None):
        if d:
            self.forward = d
            self.backward = {v: k for k, v in d.items()}
        else:
            self.forward = {}
            self.backward = {}
    
    def __setitem__(self, key, value):
        self.forward[key] = value
        self.backward[value] = key
    
    def __getitem__(self, key):
        if key in self.forward:
            return self.forward[key]
        return self.backward[key]
    
    def __contains__(self, key):
        return key in self.forward or key in self.backward
    
    def __delitem__(self, key):
        if key in self.forward:
            del self.backward[self.forward[key]]
            del self.forward[key]
        else:
            del self.forward[self.backward[key]]
            del self.backward[key]
    
    def __len__(self):
        return len(self.forward)
    
    def __iter__(self):
        return iter(self.forward)
    
    @staticmethod
    def __format__(k,v, align='left'):
        if align not in ('left', 'right'):
            raise ValueError(f"align must be 'left' or 'right', not {align}")
        
        str_left = getattr(str(k), 'ljust' if align == 'left' else 'rjust')
        str_right = getattr(str(v), 'rjust' if align == 'left' else 'ljust')
        
        return lambda l,r: f"{str_left(l)} <-> {str_right(r)}"
    
    def __repr__(self):
        output = 'bijection('
        offset = len(output)

        strings = [None for _ in self.forward]
        max_len_k = 0
        max_len_v = 0
        i = 0
        
        for k, v in self.forward.items():
            max_len_k = max(max_len_k, len(str(k)))
            max_len_v = max(max_len_v, len(str(v)))

            strings[i] = bijection.__format__(k,v, align='left')
            i += 1
        
        it = iter(map(lambda f: f(max_len_k, max_len_v), strings))
        output += next(it) + '\n'
        for s in it:
            output += (' '*offset) + s + '\n'
        output += (' '*(offset-1)) + ')'
        
        return output

# ======================================================================================================================

def get_type_name(_type: type) -> str:
    if _type is None:
        return 'None'
    elif hasattr(_type, '__name__'):
        return _type.__name__
    else:
        return str(_type)

class InitFromAnnotationsMeta(type):
    def __new__(cls, name, bases, dct):
        annotations = dct.get('__annotations__', {})

        dct['fields'] = [name for name in annotations]

        dct['not_null_fields'] = property(lambda self: [name for name in annotations if getattr(self, name) is not None])

        if annotations:
            parameters = [f'self'] + [f'{name}: {get_type_name(t)}' for name, t in annotations.items()]
            init_body = '\n    '.join([f'self.{name} = {name}' for name in annotations])

            # Default __init__
            exec_globals = globals().copy()
            default_init_definition = f"def default_init({', '.join(parameters)}):\n    {init_body}"
            exec(default_init_definition, exec_globals)
            default_init = exec_globals['default_init']

            # Is __init__ already defined?
            original_init = dct.get('__init__')

            if original_init:
                # Create a new __init__ that first calls the default and then the original
                def __init__(self, *args, **kwargs):
                    default_init(self, *args, **kwargs)
                    original_init(self, *args, **kwargs)
                dct['__init__'] = __init__
            else:
                dct['__init__'] = default_init

            # from_dict
            from_dict_body = ', '.join([f'data.get("{name}", None)' for name in annotations])
            from_dict_definition = f"@classmethod\ndef from_dict(cls, data):\n    return cls({from_dict_body})"
            exec(from_dict_definition, globals(), dct)

            # to_dict
            to_dict_body = ', '.join([f'"{name}": self.{name}' for name in annotations])
            to_dict_definition = f"def to_dict(self):\n    return {{{to_dict_body}}}"
            exec(to_dict_definition, globals(), dct)

            # Define equals method for class comparison
            #  def equals(self, other):
            #      if not isinstance(other, self.__class__):
            #          return False
            #      return all(
            #          (getattr(self, attr).equals(getattr(other, attr)) if isinstance(getattr(self, attr), AutoInit) else getattr(self, attr) == getattr(other, attr))
            #          for attr in annotations
            #      )
            #  dct['equals'] = equals

            # diff between objects. Similar to equals, but returns a list of the field names that differ.
            def diff(self, other):
                if not isinstance(other, self.__class__):
                    return list(annotations.keys())
                return [attr for attr in annotations if getattr(self, attr) != getattr(other, attr)]
            dct['diff'] = diff

            # Equals from diff == []
            def equals(self, other):
                return self.diff(other) == []
            dct['equals'] = equals

            if not '__str__' in dct:
                def __str__(self):
                    return f"{name}({', '.join([f'{name}={getattr(self, name)!r}' for name in annotations])})"
                dct['__str__'] = __str__

            if not '__repr__' in dct:
                def __repr__(self):
                    return f"{name}({', '.join([f'{name}={getattr(self, name)!r}' for name in annotations])})"
                dct['__repr__'] = __repr__

            @classmethod
            def from_other(cls, other, **kwargs):
                return cls.from_dict(**(other.to_dict()|kwargs))
            
            dct['from_other'] = from_other

            def update(self, other_or_dict, **kwargs):
                if isinstance(other_or_dict, dict):
                    keyset = set(other_or_dict)
                    annotation_set = set(annotations)
                    if not keyset.issubset(annotation_set) or not keyset == annotation_set:
                        raise ValueError(f"Invalid keys for {name}: {keyset - annotation_set}")
                    
                    for key, value in other_or_dict.items():
                        if value is not None:
                            setattr(self, key, value)
                    
                    return self
                else:
                    return self.update(other_or_dict.to_dict(), **kwargs)
            
            dct['update'] = update
            dct['__lshift__'] = update

        return super().__new__(cls, name, bases, dct)
    
class AutoInit(metaclass=InitFromAnnotationsMeta):
    pass

class Struct: ...
del Struct
Struct: type = AutoInit