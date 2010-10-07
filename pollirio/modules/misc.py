from pollirio.modules import expose

@expose('version')
def version(bot, ievent):
    bot.msg(ievent.channel, '%s: this is Pollirio, version 0.1' % ievent.nick)
