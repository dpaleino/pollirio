# -*- coding: utf-8 -*-

from pollirio.reactors import expose
from pollirio import conf, choose_dest

import random

def create_chains(lines):
    markov_chain = {}
    hasPrev = False
    for line in lines:
        for curword in line.split():
            if curword != '':
                curword = curword.lower()
                if hasPrev == False:
                    prevword = currWord
                    hasPrev = True
                else:
                    markov_chain.setdefault(prevWord, []).append(currWord)
                    prevWord = currWord
    return markov_chain
 
def make_sentence(markov_chain, words=None):
    while True:
        if not words:
            word = random.choice(markov_chain.keys())
        else:
            word = random.choice(words)
        if word[-1] not in ('.','?'):
            break
    generated_sentence = word.capitalize()
    while word[-1] not in ('.','?'):
        newword = random.choice(markov_chain[word])
        generated_sentence += ' '+newword
        word = newword #TODO fix possible crash if this is not a key (last word parsed)
    return generated_sentence

@expose('^%s' % conf.nickname)
def talk(bot, ievent):
    source = 'pg28867.txt'
    mc = create_chains(open(source))
    bot.msg(choose_dest(ievent), '%s: %s' % (ievent.nick, make_sentence(mc)))
