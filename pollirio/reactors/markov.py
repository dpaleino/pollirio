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
    markov_chains['all'] = {}
    markov_chains['fanculo'] = {}

def update_chains(lines, alternative=False):
    has_prev = False
    for line in lines:
        for cur_word in line.split():
            if cur_word != '':
                cur_word = cur_word.lower()
                if has_prev == False:
                    prev_word = cur_word
                    has_prev = True
                else:
                    if alternative:
                        markov_chains['fanculo'].setdefault(prev_word, []).append(cur_word)
                    else:
                        markov_chains['all'].setdefault(prev_word, []).append(cur_word)
                    prev_word = cur_word

def make_sentence(words=None, alternative=False):
    while True:
        if not words:
            keys = markov_chains['all'].keys()
            if alternative:
                additional_keys = [x for x in markov_chains['fanculo'].keys() if x not in keys]
                word = random.choice(keys + additional_keys)
            else:
                word = random.choice(keys)
        else:
            word = random.choice(words)
        if word[-1] not in ('.','?'):
            break
    generated_sentence = word.capitalize()
    while word[-1] not in ('.','?'):
        try:
            subchain = markov_chains['all'][word]
            if alternative:
                try:
                    additional_subchain = [x for x in markov_chains['fanculo'][word] if x not in subchain]
                except KeyError:
                    additional_subchain = []
                newword = random.choice(subchain + additional_subchain)
            else:
                newword = random.choice(subchain)
            generated_sentence += ' '+newword
            word = newword #TODO fix possible crash if this is not a key (last word parsed)
        except KeyError:
            generated_sentence += '.'
            word = '.'
    return generated_sentence

@expose('.*')
def learn(bot, ievent):
    if ievent.msg.startswith(conf.nickname) or (ievent.channel == '#fanculo' and conf.nickname in ievent.msg):
        if ievent.channel == '#fanculo':
            # learn from here too, unless a bot is speaking
            if ievent.nick not in ['godzilla', 'parrot']:
                update_chains([ievent.msg.replace(conf.nickname, '')], True)
            words = ievent.msg.replace(conf.nickname, '').split()
            talk(bot, ievent, words, True)
        else:
            talk(bot, ievent)
        return

    if ievent.channel.startswith('#'):
        if ievent.channel == '#fanculo':
            update_chains([ievent.msg], True)
        else:
            update_chains([ievent.msg])
        #print markov_chains
        cPickle.dump(markov_chains, open(markov_data, 'w'))

# commented because triggered from learn()
#@expose('^%s' % conf.nickname)
def talk(bot, ievent, words=None, alternative=False):
    #source = 'data/pg28867.txt'
    #mc = create_chains(open(source))
    bot.msg(choose_dest(ievent), '%s: %s' % (ievent.nick, make_sentence(words, alternative)))
