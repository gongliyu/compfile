User's Guide
============

.. currentmodule:: compfile

Automatically engine selection
------------------------------

Automatically engine selection is achived by :func:`auto_engine`,
which will be called in the function :func:`compfile.open`. Users
rarely need to call :func:`auto_engine` directly. 

:func:`auto_engine` will call an ordered list of engine determination
function (EDF) to decide the appropriate engine type. The signature of
a EDF must be :code:`edf_func(path: path-like)`, where :code:`path` is
the path to the archive. The function should return a callable object
if it can be determined, or return :code:`None` otherwise. The
actually engine (i.e. the callable object returned by EDF can open a
specific type of compressed file. Typical engines are
:func:`bz2.open`, :func:`gzip.open` etc.

The EDF list already contains several EDFs. Users can extend the list
by registering new EDFs:

.. code-block:: python

   arlib.register_auto_engine(func)

A priority value can also be specified:

.. code-block:: python

   arlib.register_auto_engine(func, priority)

The value of :code:`priority` define the ordering of the registered
EDFs. The smaller the :code:`priority` value, the higher the priority
values. EDFs with higher priority will be called before EDFs with
lower priority values. The default priority value is 50.

A third bool type argument :code:`prepend` can also be specified for
:func:`register_auto_engine`. When :code:`prepend` is true, the EDF will
be put before (i.e. higher priority) other registered EDFs with the
same priority value. Otherwise, it will be put after them.

:func:`register_auto_engine` can also be used as decorators

.. code-block:: python

   @compfile.register_auto_engine
   def func(path):
       # function definition

                
   @compfile.register_auto_engine(priority=50, prepend=False)
   def func2(path):
       # function definition
            
Current implementation
----------------------

Currently, the following engines are registered:

* :func:`bz2.open`
* :func:`gzip.open`
* :func:`lzma.open` for Python3 and for Python2 with lzma installed


Extend the library
------------------

The architecture of the library is flexible enough to add more
compressed file types. Adding a new compressed file type simply involves registering and EDF:

.. code-block:: python

   def open_abc(fpath, mode):
       # open the *.abc compressed file
       return uncompressed_file_file
       
   @register_auto_engine
   def edf_abc(fpath):
       if abc.endswith('.abc'):
           return open_abc
       else:
           return None
