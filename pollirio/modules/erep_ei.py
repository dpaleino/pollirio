# -*- coding: utf-8 -*-

from pollirio.modules import expose
from pollirio.dbutils import *
from pollirio import choose_dest
from pollirio import conf
from erepublik import get_uid

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
    reclute_link(bot, ievent, 'https://docs.google.com/spreadsheet/pub?key=0Al3dpy2z26cLdFp5RHBXYlhuaUo4TDdTVEc3Mk83X1E')

@expose('profilo')
def ei_profilo(bot, ievent):
    if len(ievent.args) == 0:
        user = ievent.nick
    else:
        user = ' '.join(ievent.args)
    user_id = get_uid(bot, ievent, user)
    if not user_id:
        return
    bot.msg(choose_dest(ievent), '%s: http://ei-manage.hanskalabs.net/users/view/%s' % (ievent.nick, user_id))
