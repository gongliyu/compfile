import compfile
import pytest
import os
import fnmatch
import io
import sys

_data_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')

@pytest.mark.parametrize('fname, mode',[
    ('abc.txt.bz2', 'rt'),
    ('abc.txt.gz', 'rt'),
    ('abc.txt.xz', 'rt'),
    ('abc.txt.lzma', 'rt'),
    ('abc.txt.bz2', 'rb'),
    ('abc.txt.gz', 'rb'),
    ('abc.txt.xz', 'rb'),
    ('abc.txt.lzma', 'rb'),
    ('abc.txt.lzma', 'r'),    
])
def test_compfile_open(fname, mode):
    if (not compfile._has_lzma and
        (fnmatch.fnmatch(fname, '*.lzma') or
         fnmatch.fnmatch(fname, '*.xz'))):
        return

    if sys.version_info[0] < 3 and fnmatch.fnmatch(fname, '*.bz2'):
        return
        
    fname = os.path.join(_data_path, fname)
    with compfile.open(fname, mode) as f:
        if 'b' in mode:
            f = io.TextIOWrapper(f)
        line = f.read().splitlines()
        assert line[0] == 'abc'
        assert line[1] == 'def'

