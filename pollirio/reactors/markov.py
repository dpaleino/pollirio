# -*- coding: utf-8 -*-

from pollirio.reactors import expose
from pollirio import conf, choose_dest

import random

def create_chains(lines):
    markov_chain = {}
    has_prev = False
    for line in lines:
        for cur_word in line.split():
            if cur_word != '':
                cur_word = cur_word.lower()
                if has_prev == False:
                    prev_word = cur_word
                    has_prev = True
                else:
                    markov_chain.setdefault(prev_word, []).append(cur_word)
                    prev_word = cur_word
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
    source = 'data/pg28867.txt'
    mc = create_chains(open(source))
    bot.msg(choose_dest(ievent), '%s: %s' % (ievent.nick, make_sentence(mc)))
