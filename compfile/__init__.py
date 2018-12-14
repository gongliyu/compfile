# -*- coding: utf-8 -*-

__version__ = '0.0.2'

import bz2
import gzip
import io
import os
import bisect
import fnmatch
import sys

if sys.version_info[0] >= 3 and sys.version_info[1] >= 3:
    import lzma
    _has_lzma = True
else:
    try:
        import backports.lzma as lzma
        _has_lzma = True
    except:
        _has_lzma = False


_auto_engine = []

if sys.version_info[0] >= 3 and sys.version_info[1] >= 6:
    _path_classes = (str, bytes, os.PathLike)
else:
    _path_classes = (str, bytes)


def register_auto_engine(*args, **kwargs):
    """Register automatic engine determing function
    
    Two possible signatures:

      * :code:`register_auto_engine(func, priority=50, prepend=False)`
      * :code:`register_auto-engine(priority=50, prepend=False)`

    The first one can be used as a regular function as well as a
    decorator. The second one is a decorator with arguments

    Args:

      func (callable): A callable which determines archive engine from
        file properties and open mode. The signature should be:
        func(path, mode) where path is a file-like or path-like
        object, and mode str to open the file.

      priority (int, float): Priority of the func, small number means
        higher priority. When multiple functions are registered by
        multiple call of register_auto_engine, functions will be used
        in an ordering determined by thier priortities. Default to 50.

      prepend (bool): If there is already a function with the same
        priority registered, insert to the left (before) or right
        (after) of it. Default to False.

    Return:

      The first version of signature will return the input callable
      :code:`func`, therefore it can be used as a decorator (without
      arguments). The second version will return a decorator wrap.

    """
    if len(args) + len(kwargs) == 0:
        return _register_auto_engine2()

    if len(args) > 0:
        if callable(args[0]):
            return _register_auto_engine1(*args, **kwargs)
        else:
            return _register_auto_engine2(*args, **kwargs)

    if 'func' in kwargs:
        return _register_auto_engine1(*args, **kwargs)
    else:
        return _register_auto_engine2(*args, **kwargs)


def _register_auto_engine1(func, priority=50, prepend=False):
    """Register automatic engine determining function

    Args:

      func (callable): A callable which determines archive engine from
        file properties and open mode. The signature should be:
        func(path, mode) where path is a file-like or path-like
        object, and mode str to open the file.

      priority (int, float): Priority of the func, small number means
        higher priority. When multiple functions are registered by
        multiple call of register_auto_engine, functions will be used
        in an ordering determined by thier priortities. Default to 50.

      prepend (bool): If there is already a function with the same
        priority registered, insert to the left (before) or right
        (after) of it. Default to False.

    Return:

      Callable: The object `func` is returned so that this function
        can be used as a non-argument decorator

    Note:

      This function could be used as a non-argument decorator.

    """
    p = [x[0] for x in _auto_engine]
    if prepend:
        i = bisect.bisect_left(p, priority)
    else:
        i = bisect.bisect_right(p, priority)
    _auto_engine.insert(i, (priority, func))
    return func


def _register_auto_engine2(priority=50, prepend=False):
    """Decorator with arguments for registering auto engine functions

    Args:

      priority (int, float): Priority of the func, small number means
        higher priority. When multiple functions are registered by
        multiple call of register_auto_engine, functions will be used
        in an ordering determined by thier priortities. Default to 50.

      prepend (bool): If there is already a function with the same
        priority registered, insert to the left (before) or right
        (after) of it. Default to False.

    Returns:

      A wrapper of :func:`register_auto_engine`

    See also:

      :func:`register_auto_engine`

    """
    def _decorator_wrapper(func):
        register_auto_engine(func, priority=priority, prepend=prepend)
        
    return _decorator_wrapper

@register_auto_engine(50, True)
def auto_engine_bz2(path):
    if fnmatch.fnmatch(path, '*.bz2'):
        return bz2.open
    return None

if _has_lzma:
    @register_auto_engine(50, False)
    def auto_engine_lzma(path):
        if fnmatch.fnmatch(path, '*.lzma') or fnmatch.fnmatch(path, '*.xz'):
            return lzma.open
        return None

@register_auto_engine(50, False)
def auto_engine_gzip(path):
    if fnmatch.fnmatch(path, '*.gz'):
        return gzip.open
    return None

def auto_engine(path):
    """Automatically determine engine type from file properties and file
    mode using the registered determining functions

    Args:

      path (path-like): Path to the compressed file


    Return:

      type, NoneType: a subclass of CompFile if successfully find one
        engine, otherwise None

    """
    for _, func in _auto_engine:
        engine = func(path)
        if engine is not None:
            break
    return engine

def is_compressed_file(path):
    """Infer if the file is a compressed file from file name (path-like)
    
    Args:

      path (path-like): Path to the file.

    Return:

      bool: Whether the file is a compressed file.

    Example:

      >>> is_compressed_file('a.txt.bz2')
      True
      >>> is_compressed_file('a.txt.gz')
      True
      >>> is_compressed_file('a.txt')
      False
    """
    return auto_engine(path) is not None


def open(fpath, mode, *args, **kwargs):
    """Open a compressed file as an uncompressed file stream

    Args:
    
      fpath (str): Path to the compressed file.

      mode (str): Mode arguments used to open the file. Same as :func:`open`.

    Return:

      file-object: An uncompressed file stream

    Note:

      We follow the convention of built-in function :func:`open` for
      the argument *mode* rather than the conventions of underlying
      module such as :mod:`bz2`. That's to say, we treat "r" as "rt"
      rather than "rb".
    """
    engine = auto_engine(fpath)
    # normalize mode
    mode = mode.lower()
    if 't' not in mode:
        mode += 't'
    return engine(fpath, mode, *args, **kwargs)
