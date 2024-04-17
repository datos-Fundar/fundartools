from typing import TypeVar, Generic, Iterable, Any
from collections.abc import Generator
from collections import deque
from functools import reduce as foldl
from vertexai.generative_models._generative_models import GenerationResponse, Part
from time import sleep
from IPython.display import Markdown, display, clear_output

def consume(iterator: Iterable[Any]):
    "Consume the iterator entirely."
    deque(iterator, maxlen=0)

T = TypeVar('T')
class Reference(Generic[T]):
    """
    Anotación de tipo para mostrar de forma explícita que una variable es pasada por referencia.
    """

class Copy(Generic[T]):
    """
    Anotación de tipo para mostrar de forma explícita que una variable es pasada por copia.
    """

def curry(f):
    def curried(*args):
        if len(args) == f.__code__.co_argcount:
            return f(*args)
        return lambda *more: curried(*(more + args))
    return curried

# ---------------------------------------------------------------------------------------------------

def display_result(result: Reference[list[str]]) -> Reference[list[str]]:
    sleep(0.1)
    clear_output()
    display(Markdown(''.join(result)))
    return result

def add_part(part: Part, to: Reference[list[str]]) -> Reference[list[str]]:
    """
    Toma 'to' por referencia, le agrega 'part' y devuelve la misma referencia.
    Esto es para poder encadenar aplicaciones.
    """
    to.append(part.text)
    return to

def add_part_and_display(part: Part, to: Reference[list[str]]) -> Reference[list[str]]:
    return display_result(add_part(part, to))

@curry
def add_parts_to_result(x: Iterable[Part], result: Reference[list[str]]) -> Reference[list[str]]: 
    return foldl(lambda a,b: add_part_and_display(b, add_part_and_display(a, result)  if a.text != '' else result), x, Part.from_text(''))

def get_all_parts_from_first_candidate(chunk: GenerationResponse) -> Iterable[Part]:
    return chunk.candidates[0].content.parts

def consume_chunks(generator: Generator[GenerationResponse], result=None) -> Reference[list[str]]:
    if result is None:
        result = list[str]()
        
    chunks = map(add_parts_to_result(result), map(get_all_parts_from_first_candidate, generator)) 
    consume(chunks)
    return result