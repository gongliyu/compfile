ChangeLog
=========

.. currentmodule:: compfile

0.0.2.1
-------
* Fix requirements.txt

0.0.2
-----
* Redesign: remove classes, keep :func:`compfile.open` as the public
  API (:issue:`3`, :pr:`4`).
* Add support for uncompressed file (will open use builtin
  :func:`open`), (:pr:`8`).

0.0.1
-----
* Support gz, xz, lzma, bz2 files.
* Automatic compression type deduction.
* Support open file as uncompressed streams (text and binary mode).
