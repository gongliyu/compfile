# -*- coding: utf-8 -*-

import bz2, gzip, io, os, collections, bisect, abc, fnmatch, sys

if sys.version_info[0] >= 3 and sys.version_info[1] >= 3:
    import lzma
    _has_lzma = True
else:
    try:
        import backports.lzma as lzma
        _has_lzma = True
    except:
        _has_lzma = False

__version__ = '0.0.2'

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
        return BZ2File
    return None

if _has_lzma:
    @register_auto_engine(50, False)
    def auto_engine_lzma(path):
        if fnmatch.fnmatch(path, '*.lzma') or fnmatch.fnmatch(path, '*.xz'):
            return LZMAFile
        return None

@register_auto_engine(50, False)
def auto_engine_gzip(path):
    if fnmatch.fnmatch(path, '*.gz'):
        return GzipFile
    return None

def auto_engine(path):
    """Automatically determine engine type from file properties and file
    mode using the registered determining functions

    Args:

      path (file-like, path-like): Opened file object or path to the
        archive file


    Return:

      type, NoneType: a subclass of CompFile if successfully find one
        engine, otherwise None

    """
    for _, func in _auto_engine:
        engine = func(path)
        if engine is not None:
            break
    return engine


class CompFile:
    """Common-interface to different type of compressed files manipulation

    Args:

      path (path-like, file-like): Path of the archive to read or write

      mode (str): The mode to open the member, same as in
        :func:`open`. Default to 'r'.

      \*args: Additional positional arguments passed to the underlying
        engine constructor

      engine (type): Class object of a specific subclass Archive which
        implements the logic of processing a specific type of
        Archive. Provided implements:

        * BZ2File: bz2 file
    
        * LZMAFile: lzma file

        * GzipFile: gzip file

        * None: Automatically determine engines by file properties and
          mode

      \**kwargs : Additional keyword arguments passed to the underlying
        engine constructor

    Note:

      We follow the convention of built-in function :func:`open` for
      the argument *mode* rather than the conventions of underlying
      module such as :mod:`bz2`. That's to say, we treat "r" as "rt"
      rather than "rb".

    """
    def __new__(cls, path, mode='r', *args, **kwargs):
        if cls is not CompFile:
            return object.__new__(cls)

        engine = kwargs.pop('engine', None)
        if engine is None:
            engine = auto_engine(path)
            if engine is None:
                raise RuntimeError('Cannot automatically infer engine.')

        return engine.__new__(engine, path, mode, *args, **kwargs)

    def close(self):
        self._file.close()

    @property
    def closed(self):
        return self._file.closed()

    def fileno(self):
        return self._file.fileno()

    def seekable(self):
        return self._file.seekable()

    def readable(self):
        return self._file.readable()

    def writable(self):
        return self._file.writable()

    def peek(self, n=0):
        return self._file.peek(n)

    def read(self, size=-1):
        return self._file.read(size)

    def read1(self, size=-1):
        return self._file.read1(size)

    def readinto(self, b):
        return self._file.readinto(b)

    def readline(self, size=-1):
        return self._file.readline(size)

    def readlines(self, size=-1):
        return self._file.readlines(size)

    def write(self, data):
        return self._file.write(data)

    def writelines(self, seq):
        return self._file.writelines(seq)

    def seek(self, offset, whence=io.SEEK_SET):
        return self._file.seek(offset, whence)

    def tell(self):
        return self._file.tell()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
    
class BZ2File(CompFile):
    def __init__(self, path, mode='r', *args, **kwargs):
        # normalize mode
        mode = mode.lower()
        if 't' not in mode:
            mode += 't'

        self._file = bz2.open(path, mode, *args, **kwargs)

if _has_lzma:
    class LZMAFile(CompFile):
        def __init__(self, path, mode='r', *args, **kwargs):
            mode = mode.lower()
            if 't' not in mode:
                mode += 't'
            self._file = lzma.open(path, mode, *args, **kwargs)


class GzipFile(CompFile):
    def __init__(self, path, mode='r', *args, **kwargs):
        mode = mode.lower()
        if 't' not in mode:
            mode += 't'
        self._file = gzip.open(path, mode, *args, **kwargs)

def open(*args, **kwargs):
    """Shortcut to "compfile.CompFile()"
    """
    return CompFile(*args, **kwargs)
