from ConfigParser import SafeConfigParser

class ConfReader(object):
    def __init__(self, fn):
        defaults = {
            'nick': 'pollirio',
            'channel': '#polloalforno',
        }
        self.__slots__ = defaults.keys()
        config = SafeConfigParser(defaults)
        config.read(fn)

        for name, default in defaults.iteritems():
            if type(default) == int:
                self.__dict__[name] = config.getint('global', name)
            elif type(default) == float:
                self.__dict__[name] = config.getfloat('global', name)
            else:
                self.__dict__[name] = config.get('global', name)
