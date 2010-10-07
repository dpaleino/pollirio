from pollirio.modules import expose
from pollirio import choose_dest

@expose('version')
def version(bot, ievent):
    bot.msg(choose_dest(ievent), '%s: this is Pollirio, version 0.1' % ievent.nick)
