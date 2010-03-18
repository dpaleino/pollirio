# -*- coding: utf-8 -*-

from pollirio.modules import expose

import re
import random
import os
from glob import glob
from subprocess import PIPE, Popen

path = "/usr/share/polygen/ita"
maxlen = 200

def trunc(str, length=maxlen, suffix='...'):
    if len(str) <= length:
        return str
    else:
        return ' '.join(str[:length+1].split(' ')[0:-1]) + suffix

def strip_tags(str):
    import re
    return fix_entities(re.sub(r'<[^>]*?>', ' ', str).strip())

def fix_entities(str):
    subs = {
        '&reg;' : '®',
        '&copy;': '©',
        '&trade;': '™',
        '&agrave;': 'à',
        '&aacute;': 'á',
        '&egrave;': 'è',
        '&eacute;': 'é',
        '&igrave;': 'ì',
        '&iacute;': 'í',
        '&ograve;': 'ò',
        '&oacute;': 'ó',
        '&ugrave;': 'ù',
        '&uacute;': 'ú',
    }
    for entity in subs:
        str = str.replace(entity, subs[entity])
    return str

@expose("poly")
def poly(bot, ievent):
    args = ievent.msg.split()
    try:
        grammar = "%s/%s.grm" % (path, args[1])
    except IndexError:
        grammar = None

    if not grammar:
        try:
            avail_grammars = glob("%s/*.grm" % path)
            grammar = random.choice(avail_grammars)
        except IndexError:
            bot.msg(ievent.channel, "%s: nessuna grammatica disponibile! polygen-data è installato?" % ievent.nick)
            return

    if not os.path.exists(grammar):
        bot.msg(ievent.channel, "%s: non ho la grammatica %s!" % (ievent.nick, args[1]))
        return

    try:
        p = Popen(["polygen", grammar], stdout=PIPE)
        reply = " ".join(filter(lambda x: x, p.communicate())).replace("\n", " ").strip()
        bot.msg(ievent.channel, "%s: %s" % (ievent.nick, trunc(strip_tags(reply))))
    except:
        bot.msg(ievent.channel, "%s: non posso dirti nulla di nuovo, c'è stato un errore..." % ievent.nick)
        raise
        return

@expose("poly-list")
def polylist(bot, ievent):
    try:
        grammars = glob("%s/*.grm" % path)
        tmp = []
        for g in grammars:
            tmp.append(os.path.basename(g).replace(".grm", ""))
        grammars = sorted(tmp)
    except IndexError:
        bot.msg(ievent.channel, "%s: nessuna grammatica disponibile! polygen-data è installato?" % ievent.nick)
        return

    bot.msg(ievent.channel, "%s: conosco queste grammatiche: %s" % (ievent.nick, " ".join(grammars)))
