# -*- coding: utf-8 -*-

from pollirio.reactors import expose
from pollirio import choose_dest

import random

@expose('mappina')
def mappina(bot, ievent):
	bot.msg(choose_dest(ievent), 'aaaaah, la STREGA!')

@expose('linxys')
def linxys(bot, ievent):
	bot.msg(choose_dest(ievent), 'Linxys :***')

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
	msg = random.choice(sentences)
	bot.msg(choose_dest(ievent), msg)
