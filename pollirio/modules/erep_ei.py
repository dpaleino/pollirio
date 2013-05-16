# -*- coding: utf-8 -*-

from pollirio.modules import expose
from pollirio.dbutils import *
from pollirio import choose_dest
from pollirio import conf

def reclute_link(bot, ievent, link):
    if ievent.channel not in ['#reclute-war']:
        return

    bot.sendLine('WHO %s' % ievent.channel)
    modes = bot.userlist[ievent.channel.lower()][ievent.nick]
    if '~' in modes or \
      '&' in modes or \
      '@' in modes or \
      ievent.nick == 'dapal':
        if len(ievent.args):
            nick = ievent.args[0]
        else:
            nick = ievent.nick
        bot.msg(choose_dest(ievent), '%s: %s' % (nick, link))
    return

@expose('arruola')
def arruola(bot, ievent):
    reclute_link(bot, ievent, 'http://tinyurl.com/Arruolamento')

@expose('lavoro')
def lavoro(bot, ievent):
    reclute_link(bot, ievent, 'http://tinyurl.com/LavoroEI')

@expose('equip')
def equip(bot, ievent):
    reclute_link(bot, ievent, 'http://tinyurl.com/EI-equip-160513')
