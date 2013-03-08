# -*- coding: utf-8 -*-

from pollirio.reactors import expose
from pollirio import choose_dest

@expose('mappina')
def mappina(bot, ievent):
	bot.msg(choose_dest(ievent), 'aaaaah, la STREGA!')

@expose('linxys')
def linxys(bot, ievent):
	bot.msg(choose_dest(ievent), 'Linxys :***')
