# -*- coding: utf-8 -*-

from pollirio.modules import expose
from pollirio.dbutils import *
from pollirio import choose_dest

import re
import random
import time
import exceptions

class QuotesDb:
    def __init__(self):
        self.db = db_init('quotes')

    def size(self):
        return run(self.db.count()).fetchone()[0]

    def random(self):
        quotes = run(self.db.select()).fetchall()
        if not quotes:
            return []
        else:
            return random.choice(quotes)[1]

    def idquote(self, id):
        quote = run(self.db.select(self.db.c.indx == id)).fetchone()
        if quote:
            return quote[1]

    def search(self, what):
        rs = run(self.db.select(self.db.c.quote.like('%%%s%%' % what))).fetchall()
        if rs:
            return rs

    def add(self, quote):
        rs = run(self.db.insert({'quote': unicode(quote, 'utf-8')}))
        return rs.last_inserted_ids()[0]

    def delete(self, id):
        if run(self.db.select(self.db.c.indx == id)).fetchone():
            run(self.db.delete(self.db.c.indx == id))
            return 1
        return 0

quotes = QuotesDb()

@expose('quote-size')
def quotesize(bot, ievent):
    bot.msg(choose_dest(ievent), '%s: al momento conosco \x02%s\x0F quotes.' % (ievent.nick, quotes.size()))

@expose('quote')
def quote(bot, ievent):
    '''quote [numero quote]'''
    if len(ievent.args) == 0:
        quote = quotes.random()
    else:
        try:
            quote = quotes.idquote(int(ievent.args[0]))
        except exceptions.ValueError:
            quote = quotes.random()

    if quote:
        bot.msg(choose_dest(ievent), quote.encode('utf-8'))
    else:
        bot.msg(choose_dest(ievent), '%s: non ho un quote \x02%d\x0F.' % (ievent.nick, int(ievent.args[0])))

@expose('quote-add', 1)
def quoteadd(bot, ievent):
    '''quote-add <testo>'''
    bot.sendLine('WHO %s' % ievent.channel)
    modes = bot.userlist[ievent.channel][ievent.nick]
    if '~' in modes or \
      '&' in modes or \
      '@' in modes or \
      ievent.nick == 'dapal':
        args = ievent.msg.split(' ', 1)
        id = quotes.add(args[1])
        bot.msg(choose_dest(ievent), '%s: quote \x02%s\x0F aggiunto.' % (ievent.nick, id))

@expose('quote-del', 1)
def quotedel(bot, ievent):
    '''quote-del <id>'''
    bot.sendLine('WHO %s' % ievent.channel)
    modes = bot.userlist[ievent.channel][ievent.nick]
    if '~' in modes or \
      '&' in modes or \
      '@' in modes or \
      ievent.nick == 'dapal':
        id = int(ievent.args[0])
        if quotes.delete(id):
            bot.msg(choose_dest(ievent), '%s: quote \x02%s\x0F cancellato.' % (ievent.nick, id))
        else:
            bot.msg(choose_dest(ievent), '%s: impossibile cancellare il quote %s.' % (ievent.nick, id))

@expose('quote-search', 1)
@expose('sq', 1)
def quotesearch(bot, ievent):
    '''quote-search <query>'''
    args = ievent.msg.split(' ', 1)
    query = args[1]
    for id, quote, createtime, user in quotes.search(query):
        bot.msg(choose_dest(ievent), '\x02#%s\x0F: %s' % (id, quote.encode('utf-8')))
        time.sleep(0.75)
