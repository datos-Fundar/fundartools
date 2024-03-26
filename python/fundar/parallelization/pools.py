from tqdm.contrib.concurrent import ensure_lock, thread_map as _thread_map, process_map as _process_map
from tqdm.auto import tqdm as tqdm_auto
from functools import wraps
from os import cpu_count
from concurrent.futures.process import BrokenProcessPool
import sys

def _executor(PoolExecutor, fs, **tqdm_kwargs):
    """
    Implementation of `thread_run_all` and `process_run_all`.

    Parameters
    ----------
    tqdm_class  : [default: tqdm.auto.tqdm].
    max_workers  : [default: min(32, cpu_count() + 4)].
    chunksize  : [default: 1].
    lock_name  : [default: "":str].
    """
    kwargs = tqdm_kwargs.copy()

    if "total" not in kwargs:
        kwargs["total"] = len(fs)

    tqdm_class = kwargs.pop("tqdm_class", tqdm_auto)
    max_workers = kwargs.pop("max_workers", min(32, cpu_count() + 4))
    chunksize = kwargs.pop("chunksize", 1)
    lock_name = kwargs.pop("lock_name", "")
    with ensure_lock(tqdm_class, lock_name=lock_name) as lk:
        pool_kwargs = {'max_workers': max_workers}
        sys_version = sys.version_info[:2]
        if sys_version >= (3, 7):
            # share lock in case workers are already using `tqdm`
            pool_kwargs.update(initializer=tqdm_class.set_lock, initargs=(lk,))

        with PoolExecutor(**pool_kwargs) as ex:
            futures = [ex.submit(func) for func in fs]
            return [f.result() for f in tqdm_class(futures, **kwargs)]

def _process_run_all(fs, **tqdm_kwargs):
    from concurrent.futures import ProcessPoolExecutor
    if "lock_name" not in tqdm_kwargs:
        tqdm_kwargs = tqdm_kwargs.copy()
        tqdm_kwargs["lock_name"] = "mp_lock"
    return _executor(ProcessPoolExecutor, fs, **tqdm_kwargs)


BROKEN_POOL_WIN_EXCEPTION = \
    BrokenProcessPool("If you're on Windows, the process pool has to be instantiated inside 'if __name__ == '__main__': ...'")

@wraps(_process_run_all)
def process_run_all(*args, **kwargs):
    try:
        return _process_run_all(*args, **kwargs)
    except BrokenProcessPool:
        raise BROKEN_POOL_WIN_EXCEPTION

def thread_run_all(fs, **tqdm_kwargs):
    from concurrent.futures import ThreadPoolExecutor
    if "lock_name" not in tqdm_kwargs:
        tqdm_kwargs = tqdm_kwargs.copy()
        tqdm_kwargs["lock_name"] = "thread_lock"
    return _executor(ThreadPoolExecutor, fs, **tqdm_kwargs)

thread_map = _thread_map

@wraps(_process_map)
def process_map(*args, **kwargs):
    try:
        return _process_map(*args, **kwargs)
    except BrokenProcessPool:
        raise BROKEN_POOL_WIN_EXCEPTION

def seq_run_all(fs, **tqdm_kwargs):
    kwargs = tqdm_kwargs.copy()

    if "total" not in kwargs:
        kwargs["total"] = len(fs)
        
    tqdm_class = kwargs.pop("tqdm_class", tqdm_auto)

    return list(tqdm_class([f() for f in fs], **kwargs))

def seq_map(fs, *iterables, **tqdm_kwargs):
    kwargs = tqdm_kwargs.copy()

    if "total" not in kwargs:
        kwargs["total"] = len(iterables)

    tqdm_class = kwargs.pop("tqdm_class", tqdm_auto)


    return list(tqdm_class(map(fs, *iterables), **kwargs))