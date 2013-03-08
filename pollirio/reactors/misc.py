# -*- coding: utf-8 -*-

from pollirio.reactors import expose
from pollirio import choose_dest

@expose('^notte')
@expose('^buonanotte')
def buonanotte(bot, ievent):
	bot.msg(choose_dest(ievent), '%s: notte caVo :*' % ievent.nick)
