# -*- coding: utf-8 -*-

def get_command(msg):
    # FIXME: allow a configurable control-character
    return msg.split()[0][1:]

commands = {}
