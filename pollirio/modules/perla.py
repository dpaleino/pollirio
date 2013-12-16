# -*- coding: utf-8 -*-

from pollirio.modules import expose
from pollirio.dbutils import *
from pollirio import choose_dest

import re
import random
import time
import exceptions

class PerleDb:
    def __init__(self):
        self.db = db_init('perle')

    def size(self):
        return run(self.db.count()).fetchone()[0]

    def random(self):
        perle = run(self.db.select()).fetchall()
        if not perle:
            return []
        else:
            return random.choice(perle)[1]

    def idperla(self, id):
        perla = run(self.db.select(self.db.c.indx == id)).fetchone()
        if perla:
            return perla[1]

    def search(self, what):
        rs = run(self.db.select(self.db.c.perla.like('%%%s%%' % what))).fetchall()
        if rs:
            return rs

    def add(self, perla):
        rs = run(self.db.insert({'perla': unicode(perla, 'utf-8')}))
        return rs.inserted_primary_key

    def delete(self, id):
        if run(self.db.select(self.db.c.indx == id)).fetchone():
            run(self.db.delete(self.db.c.indx == id))
            return 1
        return 0

perle = PerleDb()

@expose('perla-size')
def perlasize(bot, ievent):
    bot.msg(choose_dest(ievent), '%s: al momento conosco \x02%s\x0F perle di saggezza.' % (ievent.nick, perle.size()))

@expose('perla')
def perla(bot, ievent):
    '''perla [numero perla]'''
    if len(ievent.args) == 0:
        perla = perle.random()
    else:
        try:
            perla = perle.idperla(int(ievent.args[0]))
        except exceptions.ValueError:
            perla = perle.random()

    if perla:
        bot.msg(choose_dest(ievent), '%s: %s' % (ievent.nick, perla.encode('utf-8')))
    else:
        bot.msg(choose_dest(ievent), '%s: non esiste quella perla di saggezza!' % ievent.nick)

@expose('perla-add', 1)
def perlaadd(bot, ievent):
    '''perla-add <testo>'''
    bot.sendLine('WHO %s' % ievent.channel)
    modes = bot.userlist[ievent.channel.lower()][ievent.nick]
    if '~' in modes or \
      '&' in modes or \
      '@' in modes or \
      ievent.nick == 'dapal':
        args = ievent.msg.split(' ', 1)
        id = perle.add(args[1])
        bot.msg(choose_dest(ievent), '%s: perla \x02%s\x0F aggiunta.' % (ievent.nick, id))

@expose('perla-del', 1)
def perladel(bot, ievent):
    '''perla-del <id>'''
    bot.sendLine('WHO %s' % ievent.channel)
    modes = bot.userlist[ievent.channel.lower()][ievent.nick]
    if '~' in modes or \
      '&' in modes or \
      '@' in modes or \
      ievent.nick == 'dapal':
        id = int(ievent.args[0])
        if perle.delete(id):
            bot.msg(choose_dest(ievent), '%s: perla \x02%s\x0F cancellata.' % (ievent.nick, id))
        else:
            bot.msg(choose_dest(ievent), '%s: impossibile cancellare la perla %s.' % (ievent.nick, id))

@expose('perla-search', 1)
@expose('sp', 1)
def perlasearch(bot, ievent):
    '''perla-search <query>'''
    args = ievent.msg.split(' ', 1)
    query = args[1]
    for id, perla in perle.search(query):
        bot.msg(choose_dest(ievent), '\x02#%s\x0F: %s' % (id, perla.encode('utf-8')))
        time.sleep(0.75)
