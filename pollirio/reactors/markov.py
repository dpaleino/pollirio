# -*- coding: utf-8 -*-

from pollirio.reactors import expose
from pollirio import conf, choose_dest

import random
import cPickle

markov_data = 'data/markov.pkl'
try:
    markov_chains = cPickle.load(open(markov_data))
except IOError:
    markov_chains = {}

def update_chains(lines):
    has_prev = False
    for line in lines:
        for cur_word in line.split():
            if cur_word != '':
                cur_word = cur_word.lower()
                if has_prev == False:
                    prev_word = cur_word
                    has_prev = True
                else:
                    markov_chains.setdefault(prev_word, []).append(cur_word)
                    prev_word = cur_word

def make_sentence(words=None):
    while True:
        if not words:
            word = random.choice(markov_chains.keys())
        else:
            word = random.choice(words)
        if word[-1] not in ('.','?'):
            break
    generated_sentence = word.capitalize()
    while word[-1] not in ('.','?'):
        try:
            newword = random.choice(markov_chains[word])
            generated_sentence += ' '+newword
            word = newword #TODO fix possible crash if this is not a key (last word parsed)
        except KeyError:
            generated_sentence += '.'
            word = '.'
    return generated_sentence

@expose('.*')
def learn(bot, ievent):
    if ievent.msg.startswith(conf.nickname) or (ievent.channel == '#fanculo' and conf.nickname in ievent.msg):
        # pass control to talk()
        talk(bot, ievent)
        return
    if ievent.channel.startswith('#') and ievent.channel != '#fanculo':
        update_chains([ievent.msg])
        #print markov_chains
        cPickle.dump(markov_chains, open(markov_data, 'w'))

# commented because triggered from learn()
#@expose('^%s' % conf.nickname)
def talk(bot, ievent):
    #source = 'data/pg28867.txt'
    #mc = create_chains(open(source))
    bot.msg(choose_dest(ievent), '%s: %s' % (ievent.nick, make_sentence()))
