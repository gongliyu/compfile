*compfile* Common interfaces for manipulating compressed files (lzma, gzip etc)

[![Build Status](https://travis-ci.com/gongliyu/compfile.svg?branch=master)](https://travis-ci.com/gongliyu/compfile)
[![Documentation Status](https://readthedocs.org/projects/compfile/badge/?version=latest)](https://compfile.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/gongliyu/compfile/badge.svg?branch=master)](https://coveralls.io/github/gongliyu/compfile?branch=master)

## Rationale
Sometimes, we need to deal with different compressed files. There are
several packages/modules for compressed file manipulation, e.g.,
*gzip* module for "\*.gz" files, *lzma* module for "\*.lzma" and
"\*.xz" files, etc. If we want to support different types of
compressed file in our project, probably we need to do the following:

``` python
if fnmatch.fnmatch(fname, "*.gz"):
    f = gzip.open(fname, 'rb')
    # do something with f
elif fnmatch.fnmatch(fname, "*.bz2'):
    f = bz2.open(fname, 'rb')
    # do something with f
else:
    # other stuffs
```

The problems of the above approch are:
* We need to repeat the compression type inference logic everywhere we
  want to support different compression types.
* Different compression type manipulation modules may have different
  API convention.
  
*compfile* is designed to solve the above problems. It abstracts the logic of compressed file manipulations and provides a single high level interface for users.

## Installation

### Install from PyPI

``` shell
pip install compfile
```

### Install from Anaconda

``` shell
conda install -c liyugong compfile
```

## Simple example

Using *compfile* is pretty simple. Just construct a
*compfile.CompFile* object or call *compfile.open*

``` python
with compfile.CompFile(fname, 'r') as f:
    # do something with f
```

or 

``` python
with compfile.open(fname, 'r') as f:
    # do something with f
```

The object returned is a file object, so we can do ordinary file
processing with it.

## License

The *compfile* package is released under the [MIT License](LICENSE)

## Documentation

https://compfile.readthedocs.io

