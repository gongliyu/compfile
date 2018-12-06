User's Guide
============

.. currentmodule:: compfile

Overview
---------

*compfile* is designed using the *bridge pattern* . The abstract
compressed file manipulation functionalities (currently only open the
compressed file as a decompressed stream is implemented) are defined
in *CompFile*, an *abstract base class* called "engine". Core
functionalities are defined by the corresponding abstract methods and
properties.

The core functionalities are implemented in derived classes which we
call them *concrete engines*. Other functionalities may be overridden
by concrete engines but that's not required. Currently, three concrete
engines are implemented in the library:

* :class:`BZ2File`: Manipulates bzip2 files

* :class:`GZipFile`: Manipulates gzip files

* :class:`LZMAFile`: Manipulates lzma files

Since :class:`Archive` is a *abc*, which can not be instantiate, we
implement it as a factory to produce concrete engines instead. The
design is inspired by the :mod:`pathlib`. The type of concrete engines
are automatically determined by the archive file property and the
*mode* argument to open the archive.

A function :func:`compfile.open` is provided as a shortcut of
:class:`CompFile`.

Automatically engine selection
------------------------------

Automatically engine selection is achived by :func:`auto_engine`,
which will be called in the constructor of :class:`CompFile`. Users
rarely need to call :func:`auto_engine` directly. Call the constructor
of :class:`CompFile` or :func:`compfile.open` will implicitely call
:func:`auto_engine`.

:func:`auto_engine` will call an ordered list of engine determination
function (EDF) to decide the appropriate engine type. The signature of
a EDF must be :code:`edf_func(path: path-like)`, where :code:`path` is
the path to the archive. The function should return a concrete engine
type if it can be determined, or return :code:`None` otherwise.

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

Since :func:`register_auto_engine` returns the input function object
:code:`func`, it can also be used as a non-parameterized decorator:

.. code-block:: python

   @compfile.register_auto_engine
   def func(path, mode):
       # function definition

The function :func:`register_auto_engine` also support another version of calling signature :code:`arlib.register_auto_engine(priority, prepend)`, which will return a wrapped decorator with arguments. The typical usage is:

.. code-block:: python
                
   @compfile.register_auto_engine(priority=50, prepend=False)
   def func(path, mode):
       # function definition
            
Current implementation
----------------------

Currently, concrete engines are also derived from the classes from
underlying module. For example, :class:`compfile.BZ2File` is derived
from :class:`bz2.BZ2File`. So it inheriate all methods from the super
class, including all file-like functionalities.


Extend the library
------------------

The architecture of the library is flexible enough to add more archive
types. Adding a new archive type includes the following steps:

#. Derive a new class and implement the file-like functionalities or
   inheritate from a file like class

   .. code-block:: python

      class AnotherArchive(Archive):
          def __init__(self, path, mode, **kwargs):
              # definition

#. (optional) defined and register a new EDF which could automatically
   determine the new compressed file type

   .. code-block:: python

      @register_auto_engine
      def another_auto_engine(path):
          # definition
