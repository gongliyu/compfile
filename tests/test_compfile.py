import compfile, pytest, os

_data_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')

@pytest.mark.parametrize('fname',[
    'abc.txt.bz2',
    'abc.txt.gz',
    'abc.txt.xz',
    'abc.txt.lzma'
])
def test_compfile_open(fname):
    fname = os.path.join(_data_path, fname)
    with compfile.open(fname, 'rt') as f:
        assert f.readline() == 'abc\n'

