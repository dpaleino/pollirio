# -*- coding: utf-8 -*-

from pollirio.reactors import expose
from pollirio import choose_dest

import random

def randomize_msg(sentences):
    times = len(sentences) * 5
    while times > 0:
        index = random.randint(0, len(sentences) - 1)
        sentences.insert(index, None)
        times -= 1
    return random.choice(sentences)

@expose('mappina')
def mappina(bot, ievent):
    bot.msg(choose_dest(ievent), 'aaaaah, la STREGA!')

@expose('linxys')
def linxys(bot, ievent):
    sentences = [
        'Linxys :***',
        'Linxys ti difendo io!',
        'hey, Linxys! Non tradirmi! :(',
    ]
    msg = randomize_msg(sentences)
    if msg:
        bot.msg(choose_dest(ievent), msg)

@expose(r'\bturid\b')
def turid(bot, ievent):
    sentences = [
        'che ha combinato Turid stavolta?!',
        'ma Turid ha bevuto?',
        'in alto i calici per Turid!',
        'evviva Turid!!!',
        'fate reclutare gente a Turid!',
        'Turid mi fa i dispetti :(',
        'Turid: ILLIMITATAMENTEEEEEEE',
    ]
    msg = randomize_msg(sentences)
    if msg:
        bot.msg(choose_dest(ievent), msg)

@expose('x3rr3x')
@expose(r'\berre\b')
def erre(bot, ievent):
    sentences = [
        'vola, x3rr3x, vola!',
        'x3rr3x sei carico stasera?',
    ]
    msg = randomize_msg(sentences)
    if msg:
        bot.msg(choose_dest(ievent), msg)
