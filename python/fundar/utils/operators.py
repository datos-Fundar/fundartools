import operator
from fundar.utils import curry

__all__ = operator.__all__

def __getattr__(name):
    return curry(getattr(operator, name))
    
    