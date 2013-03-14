# -*- coding: utf-8 -*-

from pollirio.modules import expose
from pollirio.dbutils import *
from pollirio import choose_dest
from pollirio import conf

import cjson as json
from urllib2 import urlopen
from datetime import datetime

class UsersDb:
	def __init__(self):
		self.db = db_init('erep_users')

	def search(self, what):
		rs = run(self.db.select(self.db.c.username.like('%s' % what))).fetchall()
		return rs

	def add(self, username, user_id):
		rs = run(self.db.insert({
			'username': unicode(username, 'utf-8'),
			'user_id': str(int(user_id))
		}))
		return rs.last_inserted_ids()[0]

users = UsersDb()

api_key = conf.config.get('erepublik', 'api_key')
api_url = conf.config.get('erepublik', 'api_url')

def request(resource, **args):
	format = 'json' # or 'xml'
	patterns = {
		'citizen.profile': 'citizen/profile/%(id)d',
		'citizen.search': 'citizen/search/%(query)s/%(page)d',
		'battle.active': 'battle/active',
		'battle': 'battle/%(id)d',
		'country.society': 'country/%(country)s/society',
		'country.economy': 'country/%(country)s/economy',
		'party': 'party/%(id)d',
		'mu': 'mu/%(id)d',
		'mu.regiment': 'mu/%(id)d/%(regiment)d',
		'market': 'market/%(country)s/%(industry)s/%(quality)d/%(page)d',
		'job.market': 'jobmarket/%(country)s/%(page)d',
		'exchange': 'exchange/%(mode)d/%(page)d',
		'election.president': 'election/president/%(year)d/%(month)d/%(country)s',
		'election.congress': 'election/congress/%(year)d/%(month)d/%(country)s/%(region)s',
		'election.party': 'election/congress/%(year)d/%(month)d/%(country)s/%(party)d',
		
	}
	if resource not in patterns:
		return None
	ret = urlopen(api_url + patterns[resource] % args + '.json?key=%s' % api_key)
	return json.decode(''.join(ret.readlines()))

def get_uid(bot, ievent, user):
	ret = users.search(user)
	if ret:
		return ret[3]
	data = request('citizen.search', query=user.replace(' ', '_'), page=1)
	if data:
		uid = data[0]['id']
		users.add(user, uid)
		return uid
	else:
		bot.msg(choose_dest(ievent), '%s: utente «%s» non trovato.' % (ievent.nick, user))
		return None
	
@expose('lp')
def list_profile(bot, ievent):
	if len(ievent.args) == 0:
		user = ievent.nick
	else:
		user = ' '.join(ievent.args)
	user_id = get_uid(bot, ievent, user)
	if not user_id:
		return
	profile = request('citizen.profile', id=user_id)
	age = datetime.now() - datetime.strptime(profile['birth'], '%Y-%m-%d')
	bot.msg(
		choose_dest(ievent),
		'\x02ID:\x0F %s ' \
		'\x02Lvl:\x0F %s ' \
		'\x02Age:\x0F %s ' \
		'\x02XP:\x0F %s ' \
		'\x02Strength:\x0F %s ' \
		'\x02Rank:\x0F %s ' \
		'\x02Rank Points:\x0F %s ' \
		'\x02Ranking:\x0F %s ' \
		'\x02CZ:\x0F %s ' \
		'\x02Residence:\x0F %s, %s ' \
		'\x02Party:\x0F %s ' \
		'\x02MU:\x0F %s' %
		(
			user_id,
			profile['level'],
			age.days,
			profile['experience'],
			profile['strength'],
			profile['rank']['name'],
			profile['rank']['points'],
			profile['national_rank'],
			profile['citizenship']['name'],
			profile['residence']['country']['name'],
			profile['residence']['region']['name'],
			profile['party']['name'],
			profile['army']['name']
		)
	)

@expose('fc')
def fight_calc(bot, ievent):
	if len(ievent.args) == 0:
		user = ievent.nick
	else:
		user = ' '.join(ievent.args)
	user_id = get_uid(bot, ievent, user)
	if not user_id:
		return
	profile = request('citizen.profile', id=user_id)
	hit = int(profile['hit'])
	bot.msg(
		choose_dest(ievent),
		'%s: Inf Q0: \x02%s\x0F :: Q1: \x02%s\x0F :: Q2: \x02%s\x0F :: Q3: \x02%s\x0F :: Q4: \x02%s\x0F :: Q5: \x02%s\x0F :: Q6: \x02%s\x0F :: Q7: \x02%s\x0F' % \
		(ievent.nick, hit, int(hit*1.2), int(hit*1.4), int(hit*1.6), int(hit*1.8), hit*2, int(hit*2.2), hit*3)
	)

@expose('link')
def link_profile(bot, ievent):
	if len(ievent.args) == 0:
		user = ievent.nick
	else:
		user = ' '.join(ievent.args)
	user_id = get_uid(bot, ievent, user)
	if not user_id:
		return
	bot.msg(choose_dest(ievent), '%s: http://www.erepublik.com/en/citizen/profile/%s' % (ievent.nick, user_id))

@expose('donate')
def link_profile(bot, ievent):
	if len(ievent.args) == 0:
		user = ievent.nick
	else:
		user = ' '.join(ievent.args)
	user_id = get_uid(bot, ievent, user)
	if not user_id:
		return
	bot.msg(choose_dest(ievent), '%s: http://www.erepublik.com/en/economy/donate-items/%s' % (ievent.nick, user_id))
