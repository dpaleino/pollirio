
def test_confreader():
    from pollirio.confreader import ConfReader
    conf = ConfReader('tests/test.ini')
    assert conf.channel == '#polloalforno'
    assert conf.server_addr == 'calvino.freenode.net'
    assert conf.server_port == 6667

#def setup_lart():
#    from pollirio.modules.lart import *
#
#def test_lart():
#    pass
#
#test_lart.setUp = setup_lart
