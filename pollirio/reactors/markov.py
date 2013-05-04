# -*- coding: utf-8 -*-

from pollirio.reactors import expose
from pollirio import conf, choose_dest

import random
import cPickle
import string

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
                    if prev_word == cur_word:
                        # avoid infinite loops
                        continue
                    chain = 'all'
                    if alternative:
                        chain = 'fanculo'
                    if prev_word in markov_chains[chain]:
                        if cur_word in markov_chains[chain][prev_word]:
                            markov_chains[chain][prev_word][cur_word] += 1
                        else:
                            markov_chains[chain][prev_word][cur_word] = 1
                    else:
                        markov_chains[chain][prev_word] = {cur_word: 1}
                    #~ markov_chains[chain].setdefault(prev_word, []).append(cur_word)

                    prev_word = cur_word

def make_sentence(words=None, alternative=False):
    while True:
        if not words:
            keys = markov_chains['all'].keys()
            additional_keys = []
            if alternative:
                additional_keys = [x for x in markov_chains['fanculo'].keys() if x not in keys]
            word = random.choice(keys + additional_keys)
        else:
            word = random.choice(words)
        if word[-1] not in ('.','?'):
            break
    generated_sentence = word.capitalize()
    while word[-1] not in ('.','?'):
        try:
            threshold = int(round(sum(markov_chains['all'][word].values()) / (len(markov_chains['all'][word].values()) * 1.0)))
            subchain = [x[0] for x in markov_chains['all'][word].items() if x[1] >= threshold]
            try:
                subchain.remove(word)
            except ValueError:
                pass
            additional_subchain = []
            if alternative:
                try:
                    additional_subchain = [x[0] for x in markov_chains['fanculo'][word].items() if x[0] not in subchain and x[1] >= threshold]
                    try:
                        additional_subchain.remove(word)
                    except ValueError:
                        pass
                except KeyError:
                    pass
            newword = random.choice(subchain + additional_subchain)
            generated_sentence += ' '+newword
            word = newword #TODO fix possible crash if this is not a key (last word parsed)
        except (KeyError, IndexError):
            generated_sentence += '.'
            word = '.'
    return generated_sentence

@expose('.*')
def learn(bot, ievent):
    if ievent.msg.startswith(conf.nickname) or (ievent.channel == '#fanculo' and conf.nickname in ievent.msg):
        punct = string.punctuation.replace('_', '')
        punct = punct.replace('|', '')
        punct = punct.replace('-', '')
        msg = ievent.msg.translate(string.maketrans('', ''), punct)
        words = msg.replace(conf.nickname, '').split()

        if ievent.channel == '#fanculo':
            # learn from here too, unless a bot is speaking
            if ievent.nick not in ['godzilla', 'parrot', 'RedBot']:
                update_chains([ievent.msg.replace(conf.nickname, '')], True)
            talk(bot, ievent, words, True)
        else:
            talk(bot, ievent, words)
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
