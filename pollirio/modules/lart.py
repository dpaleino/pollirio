# -*- coding: utf-8 -*-

from pollirio.modules import expose
from pollirio.dbutils import *

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
        rs = run(self.db.insert({"lart": lart}))
        return rs.last_inserted_ids()[0]

    def delete(self, id):
        if run(self.db.select(self.db.c.indx == id)).fetchone():
            run(self.db.delete(self.db.c.indx == id))
            return 1
        return 0

larts = LartsDb()

@expose("lart", 1)
@expose("larta", 1)
def lart(bot, ievent):
    """lart <utente> [numero lart]"""

    if len(ievent.args) == 1:
        lart = larts.random()
    else:
        try:
            lart = larts.idlart(int(ievent.args[1]))
        except exceptions.ValueError:
            lart = larts.random()

    if not lart:
        bot.msg(ievent.channel, "%s autolartati, non esiste quel lart!" % ievent.nick)
        return

    lart = lart.replace("$who", ievent.args[0]).encode("utf-8")
    bot.describe(ievent.channel, lart)
    return

@expose("lartami")
@expose("autolart")
def selflart(bot, ievent):
    ievent.msg = ".lart %s" % ievent.nick
    lart(bot, ievent)

@expose("lart-add", 1)
def lartadd(bot, ievent):
    """lart-add <testo contenente $who>"""
    args = ievent.msg.split(" ", 1)
    if len(args) == 1:
        bot.msg(ievent.channel, "%s: cosa devo aggiungere?" % ievent.nick)
        return

    id = larts.add(args[1])
    bot.msg(ievent.channel, "%s: lart %s aggiunto." % (ievent.nick, id))
    return

@expose("lart-del", 1)
def lartdel(bot, ievent):
    """lart-del <id del lart>"""
    if not ievent.args:
        bot.msg(ievent.channel, "%s: cosa devo cancellare?" % ievent.nick)
        return

    id = int(ievent.args[0])
    if larts.delete(id):
        bot.msg(ievent.channel, "%s: lart %s cancellato." % (ievent.nick, id))
    else:
        bot.msg(ievent.channel, "%s: impossibile cancellare lart %s." % (ievent.nick, id))
    return

@expose("lart-search", 1)
@expose("sl", 1)
def lartsearch(bot, ievent):
    """lart-search <query>"""
    args = ievent.msg.split(" ", 1)
    if len(args) == 1:
        bot.msg(ievent.channel, "%s: cosa devo cercare?" % ievent.nick)
        return

    query = args[1]
    for id, lart in larts.search(query):
        bot.msg(ievent.channel, "#%s: %s" % (id, lart.encode("utf-8")))
        time.sleep(0.75)
    return

@expose("lart-size")
def lartsize(bot, ievent):
    bot.msg(ievent.channel, "%s: al momento conosco %s lart." % (ievent.nick, larts.size()))
    return
