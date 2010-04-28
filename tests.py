
def test_confreader():
    from pollirio.confreader import ConfReader
    conf = ConfReader('tests/test.ini')
    assert conf.channel == '#polloalforno'
