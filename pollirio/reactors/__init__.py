# -*- coding: utf-8 -*-

from functools import wraps
from pollirio import reactors

import re

def expose(text, args=None):
    def decorator(fn):
        reactors[text] = {"func":fn, "args":args}
        return fn
    return decorator

def reactor_run(line, *args):
    for k in reactors.keys():
        if re.findall(k, line):
            return reactors.get(k)["func"](*args)

from users import *
from misc import *
