# -*- coding: utf-8 -*-

from functools import wraps
from pollirio import commands

def old_expose(cmd):
    def inner(fn):
        def wrapped(*args, **kwargs):
            commands[cmd] = fn
            fn(*args)
        return wraps(fn)(wrapped)
    return inner

def expose(cmd, args=None):
    def decorator(fn):
        commands[cmd] = {"func":fn, "args":args}
        return fn
    return decorator

def plugin_run(name, *args):
    if name in commands:
        return commands.get(name)["func"](*args)

def check_args(name, bot, ievent):
    if name in commands:
        if commands.get(name)["args"]:
            # TODO: check if we have all the arguments
            print len(ievent.args), commands.get(name)["args"]
            if len(ievent.args) < commands.get(name)["args"]:
                bot.msg(ievent.channel, "%s: %s" % (ievent.nick, commands.get(name)["func"].__doc__))
                return False
            else:
                return True
        else:
            return True
    return False

from lart import *
from polygen import *
#from bts import *
from misc import *
