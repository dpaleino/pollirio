from ConfigParser import SafeConfigParser

class ConfReader(object):
    def __init__(self, fn):
        defaults = {
            'nickname': 'pollirio',
            'password': '',
            'channels': '#polloalforno',
            'server_addr': 'calvino.freenode.net',
            'server_port': 6667,
        }
        self.__slots__ = defaults.keys()
        self.config = SafeConfigParser(defaults)
        self.config.read(fn)

        for name, default in defaults.iteritems():
            if type(default) == int:
                self.__dict__[name] = self.config.getint('global', name)
            elif type(default) == float:
                self.__dict__[name] = self.config.getfloat('global', name)
            else:
                self.__dict__[name] = self.config.get('global', name)
