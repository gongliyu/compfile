# -*- coding: utf-8 -*-

__version__ = '0.0.2'

import bz2
import gzip
import io
import os
import bisect
import fnmatch
import sys

import decoutils

_builtin_open = open

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


@decoutils.decorator_with_args(True)
def register_auto_engine(func, priority=50, prepend=False):
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
    p = [x[0] for x in _auto_engine]
    if prepend:
        i = bisect.bisect_left(p, priority)
    else:
        i = bisect.bisect_right(p, priority)
    _auto_engine.insert(i, (priority, func))


@register_auto_engine(prepend=True)
def auto_engine_bz2(path):
    if fnmatch.fnmatch(path, '*.bz2'):
        return _open_bz2
    return None

def _open_bz2(fpath, mode='r', compresslevel=9,  encoding=None,
              errors=None, newline=None):
    if 'b' not in mode:
        mode2 = mode.replace('t', '') if 't' in mode else mode
        f = bz2.BZ2File(fpath, mode2, compresslevel=compresslevel)
        f =  io.TextIOWrapper(f, encoding, errors, newline)
    else:
        f = bz2.BZ2File(fpath, mode, compresslevel)
    return f
        

if _has_lzma:
    @register_auto_engine
    def auto_engine_lzma(path):
        if fnmatch.fnmatch(path, '*.lzma') or fnmatch.fnmatch(path, '*.xz'):
            return lzma.open
        return None

@register_auto_engine
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
    if engine is None:
        return _builtin_open(fpath, mode, *args, **kwargs)
    # normalize mode
    mode = mode.lower()
    if 't' not in mode and 'b' not in mode:
        mode += 't'
    return engine(fpath, mode, *args, **kwargs)
