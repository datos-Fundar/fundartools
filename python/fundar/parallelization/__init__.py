from typing import Callable, Iterable, TypeVar, Any
from .pools import *

A = TypeVar('A')
B = TypeVar('B')
class Executor:
    run_all: Callable
    run_map: Callable

    @classmethod
    def execute(cls, fs: Iterable[Callable[[], A]], **tqdm_kwargs) -> list[A]:
        """
        Executes a list of functions with void arguments and returns their results in order.
        """
        return cls.run_all(fs, **tqdm_kwargs)

    @classmethod
    def map(cls, fn: Callable[[A], B], *iterables: A, **tqdm_kwargs) -> list[B]:
        """
        Maps and executes a function over variadic arguments and returns the results in order.
        """
        return cls.run_map(fn, *iterables, **tqdm_kwargs)
    
class Multithread(Executor):
    """
    Executes actions using multiple threads.
    """

    run_all = thread_run_all
    run_map = thread_map

class Multiprocess(Executor):
    """
    Executes actions using multiple processes.
    """
    run_all = process_run_all
    run_map = process_map

class Sequentially(Executor):
    """
    Executes actions sequentially (single-thread, single-process).
    """
    run_all = seq_run_all
    run_map = seq_map