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

def expose(cmd):
    def decorator(fn):
        commands[cmd] = fn
        return fn
    return decorator

def run(name, *args):
    if name in commands:
        return commands.get(name)(*args)

from lart import *
