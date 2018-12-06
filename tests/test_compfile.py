import compfile, pytest, os, fnmatch

_data_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')

@pytest.mark.parametrize('fname',[
    'abc.txt.bz2',
    'abc.txt.gz',
    'abc.txt.xz',
    'abc.txt.lzma'
])
def test_compfile_open(fname):
    if not compfile._has_lzma and (fnmatch.fnmatch(fname, '*.lzma') or
                                   fnmatch.fnmatch(fname, '*.xz')):
        return
        
    fname = os.path.join(_data_path, fname)
    with compfile.CompFile(fname, 'rt') as f:
        assert f.readline() == 'abc\n'

