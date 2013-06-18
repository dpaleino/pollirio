# -*- coding: utf-8 -*-

from pollirio.modules import expose
from pollirio.dbutils import *
from pollirio import choose_dest

import re
import random
import time
import exceptions

class LartsDb:
    def __init__(self):
        self.db = db_init("larts")

    def size(self):
        return run(self.db.count()).fetchone()[0]

    def random(self):
        larts = run(self.db.select()).fetchall()
        if not larts:
            return []
        else:
            return random.choice(larts)[1]

    def idlart(self, id):
        lart = run(self.db.select(self.db.c.indx == id)).fetchone()
        if lart:
            return lart[1]

    def search(self, what):
        rs = run(self.db.select(self.db.c.lart.like("%%%s%%" % what))).fetchall()
        if rs:
            return rs

    def add(self, lart):
        rs = run(self.db.insert({"lart": unicode(lart, 'utf-8')}))
        return rs.last_inserted_ids()[0]

    def delete(self, id):
        if run(self.db.select(self.db.c.indx == id)).fetchone():
            run(self.db.delete(self.db.c.indx == id))
            return 1
        return 0

class LartIgnoreDb:
    def __init__(self):
        self.db = db_init("lartignore")

    def ignored(self, src, dst):
        r = run(self.db.select(and_( \
            self.db.c.src.like("%%%s%%" % src), \
            self.db.c.dst.like("%%%s%%" % dst)
        ))).fetchall()
        if r:
            return True
        return False

    def add(self, src, dst):
        rs = run(self.db.insert({"src": src, "dst": dst}))
        return rs.last_inserted_ids()[0]

    def delete(self, src, dst):
        r = run(self.db.delete().where(and_( \
            (self.db.c.src == src),
            (self.db.c.dst == dst) \
        ))).fetchone()
        if r:
            return 1
        return 0

larts = LartsDb()
ignores = LartIgnoreDb()

@expose("lart", 1)
@expose("larta", 1)
def lart(bot, ievent):
    """lart <utente> [numero lart]"""

    if len(ievent.args):
        if ignores.ignored(ievent.nick, ievent.args[0]):
            return

    if len(ievent.args) == 1:
        lart = larts.random()
    else:
        try:
            lart = larts.idlart(int(ievent.args[1]))
        except exceptions.ValueError:
            lart = larts.random()

    if re.match('.*!.*@unaffiliated/damn3dg1rl', ievent.host) or \
       ievent.nick == 'DAMN3dg1rl':
       ievent.args[0] = ievent.nick

    if not lart:
        bot.msg(ievent.channel, "%s autolartati, non esiste quel lart!" % ievent.nick)
        return

    lart = lart.replace("$who", ievent.args[0]).encode("utf-8")
    bot.describe(ievent.channel, lart)
    return

@expose("lartignore", 1)
def lartignore(bot, ievent):
    """lartignore <utente>"""
    bot.sendLine('WHO %s' % ievent.channel)
    modes = bot.userlist[ievent.channel.lower()][ievent.nick]
    if '~' in modes or \
      '&' in modes or \
      '@' in modes or \
      ievent.nick == 'dapal':
        if len(ievent.args):
            ignores.add(ievent.args[0], ievent.nick)
            bot.msg(choose_dest(ievent), '%s: cot' % ievent.nick)
    return

@expose("lartallow", 1)
def lartllow(bot, ievent):
    """lartallow <utente>"""
    bot.sendLine('WHO %s' % ievent.channel)
    modes = bot.userlist[ievent.channel.lower()][ievent.nick]
    if '~' in modes or \
      '&' in modes or \
      '@' in modes or \
      ievent.nick == 'dapal':
        if len(ievent.args):
            ignores.delete(ievent.args[0], ievent.nick)
            bot.msg(choose_dest(ievent), '%s: cot' % ievent.nick)
    return

@expose("lartami")
@expose("autolart")
def selflart(bot, ievent):
    ievent.args = [ievent.nick] + ievent.msg.split()[1:]
    lart(bot, ievent)

@expose("lart-add", 1)
def lartadd(bot, ievent):
    """lart-add <testo contenente $who>"""
    args = ievent.msg.split(" ", 1)
    bot.sendLine('WHO %s' % ievent.channel)
    modes = bot.userlist[ievent.channel.lower()][ievent.nick]
    if '~' in modes or \
      '&' in modes or \
      '@' in modes or \
      ievent.nick == 'dapal':
        id = larts.add(args[1])
        bot.msg(choose_dest(ievent), "%s: lart %s aggiunto." % (ievent.nick, id))
    return

@expose("lart-del", 1)
def lartdel(bot, ievent):
    """lart-del <id del lart>"""
    bot.sendLine('WHO %s' % ievent.channel)
    modes = bot.userlist[ievent.channel.lower()][ievent.nick]
    if '~' in modes or \
      '&' in modes or \
      '@' in modes or \
      ievent.nick == 'dapal':
        id = int(ievent.args[0])
        if larts.delete(id):
            bot.msg(choose_dest(ievent), "%s: lart %s cancellato." % (ievent.nick, id))
        else:
            bot.msg(choose_dest(ievent), "%s: impossibile cancellare lart %s." % (ievent.nick, id))
    return

@expose("lart-search", 1)
@expose("sl", 1)
def lartsearch(bot, ievent):
    """lart-search <query>"""
    args = ievent.msg.split(" ", 1)
    if len(args) == 1:
        bot.msg(choose_dest(ievent), "%s: cosa devo cercare?" % ievent.nick)
        return

    query = args[1]
    if len(query) < 3:
        bot.msg(choose_dest(ievent), '%s: il termine di ricerca deve contenere almeno 3 caratteri.')
        return
    for id, lart in larts.search(query):
        bot.msg(choose_dest(ievent), "#%s: %s" % (id, lart.encode("utf-8")))
        time.sleep(0.75)
    return

@expose("lart-size")
def lartsize(bot, ievent):
    bot.msg(choose_dest(ievent), "%s: al momento conosco %s lart." % (ievent.nick, larts.size()))
    return
