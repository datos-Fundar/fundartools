from .utils import callx
from functools import reduce, wraps

class List(list):
    """
    Subclase del primitivo 'list', con métodos adicionales para una manipulación de listas más funcional.
    En particular, convierte algunas operaciones lazy (map, filter, reduce) y las hace eager.
    """

    def map(self, f):
        """
        Versión eager de map.
        """
        return List(map(f, self))

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
    
    def find(self, f):
        """
        Devuelve x tal que f(x) == True, si existe, o una lista vacía en caso contrario.
        """
        matches = self.filter(f)
        return matches[0] if matches else []
    
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
    
    @wraps(list.sort)
    def sort(self, **kwargs):
        self = List(sorted(self, **kwargs))
        return self
    
    def __getitem__(self, index):
        if isinstance(index, slice):
            return List(super().__getitem__(index))
        return super().__getitem__(index)
