# -*- coding: utf-8 -*-

from confreader import ConfReader

conf = ConfReader('pollirio.ini')
commands = {}

def get_command(msg):
    # FIXME: allow a configurable control-character
    if msg[0] == '.':
        return msg.split()[0][1:]
    else:
        return msg.split()[0]

def choose_dest(ievent):
    if ievent.channel == conf.nickname:
        return ievent.nick
    else:
        return ievent.channel

