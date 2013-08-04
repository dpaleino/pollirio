# -*- coding: utf-8 -*-

from pollirio.modules import expose
from pollirio import choose_dest
from pollirio import conf

@expose('mass')
def mass(bot, ievent, msg=None):
    if ievent.channel == conf.nickname:
        return
    bot.sendLine('WHO %s' % ievent.channel)
    modes = bot.userlist[ievent.channel.lower()][ievent.nick]
    if '~' in modes or \
      '&' in modes or \
      '@' in modes or \
      '%' in modes or \
      ievent.nick == 'dapal':
        users = sorted(bot.userlist[ievent.channel.lower()].keys())
        bot.msg(ievent.channel, ' '.join(users))
        if msg:
            bot.msg(ievent.channel, '\x02%s\x0F' % msg)

@expose('call', 1)
def call(bot, ievent):
    """ call <messaggio> """
    if ievent.channel == conf.nickname:
        return

    args = ievent.msg.split(' ', 1)
    mass(bot, ievent, msg=args[1])
