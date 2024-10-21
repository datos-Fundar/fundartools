"""
This type stub file was generated by pyright.
"""

import uuid
from langchain.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from collections.abc import Iterable
from typing import Optional, Sequence, TypeVar

T = TypeVar('T')
def flatten(nested_list: Sequence[Sequence[T]], max_level=...) -> Sequence[T]:
    ...

def split_list_into_chunks(lst: list[T], chunk_size: int): # -> list[list[T]]:
    ...

def pass_generator_as_copy(*xs): # -> Callable[..., _Wrapped[Callable[..., Any], Any, Callable[..., Any], Any]]:
    ...

def allow_opaque_constructor(**objects): # -> Callable[..., _Wrapped[Callable[..., Any], Any, Callable[..., Any], Any]]:
    ...

def consume(iterator, n=...): # -> None:
    "Advance the iterator n-steps ahead. If n is none, consume entirely."
    ...

_is_cuda_available_ = ...
def is_cuda_available() -> bool:
    ...

class UuidGenerator:
    def __init__(self, seed: Optional[int] = ...) -> None:
        ...
    
    def reset(self): # -> Self:
        ...
    
    def next(self, n: Optional[int] = ...): # -> UUID | Generator[UUID, None, None]:
        ...
    
    def __iter__(self): # -> Generator[UUID | Generator[UUID, None, None], Any, NoReturn]:
        ...
    
    @pass_generator_as_copy('xs')
    def map(self, xs: Iterable[T], offset: Optional[int] = ...) -> Iterable[uuid.UUID]:
        ...
    
    @pass_generator_as_copy('xs')
    def zipWith(self, xs: Iterable[T], offset: Optional[int] = ...) -> Iterable[tuple[uuid.UUID, T]]:
        ...
    


DEFAULT_PDF_LOADER = PyPDFLoader
def load_document(filepath: str, loader=..., seed_id: Optional[int] = ...) -> list[Document]:
    ...

DEFAULT_RCT_SPLITTER = ...
@allow_opaque_constructor(splitter=RecursiveCharacterTextSplitter)
def split_document(xs, splitter=..., seed_id: Optional[int] = ...) -> list[Document]:
    ...

def load_and_split(filepath: str, loader=..., splitter=..., seed_id: Optional[int] = ..., flatten=...): # -> list[Document] | list[list[Document]]:
    ...

_sentence_transformer_obj = ...
def SentenceTransformer(*args, **kwargs): # -> SentenceTransformer:
    """
    Default args:
        - model: sentence-transformers/all-mpnet-base-v2
        - device: auto (cuda if available)
    """
    ...

def encode_with_multiprocessing(transformer, pool): # -> Callable[..., NDArray[Any]]:
    ...

@allow_opaque_constructor(sentence_transformer=SentenceTransformer)
def vectorize_document(x: str | Document | Iterable[Document | str], sentence_transformer=..., uid=..., additional_metadata=..., devices=...): # -> list[dict[str, List[Tensor] | ndarray[Any, Any] | Tensor | NDArray[Any] | Any]] | list[dict[str, Document | str | dict[Any, Any] | UUID | Tensor]]:
    ...

def available_vram_nvidia_smi(): # -> tuple[int, int]:
    ...

def available_vram_torch(): # -> tuple[int, Any]:
    ...

def get_available_vram(): # -> tuple[int, int] | tuple[int, Any]:
    ...

def splitmodel(x) -> tuple[str, str]:
    ...

def modelname(x): # -> str:
    ...

def modelspecs(x): # -> str:
    ...

