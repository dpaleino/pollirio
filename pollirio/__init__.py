# -*- coding: utf-8 -*-

def get_command(msg):
    # FIXME: allow a configurable control-character
    if msg[0] == '.':
        return msg.split()[0][1:]
    else:
        return msg.split()[0]

commands = {}
