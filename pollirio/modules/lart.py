# -*- coding: utf-8 -*-

from pollirio.modules import expose

@expose("lart")
@expose("larta")
def lart(bot, ievent):
    bot.msg(ievent.channel, "..executing lart..")
    return

@expose("picchia")
def picchia(bot, ievent):
    bot.msg(ievent.channel, "Chi vuoi picchiare?")
    return
