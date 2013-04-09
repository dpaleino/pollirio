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
        return int(ret[0][2])
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

    if not profile['party']:
        profile['party']= {'name': 'Nessun partito'}
    if not profile['army']:
        profile['army'] = {'name': 'Nessuna MU'}

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

@expose('egov')
def egov_profile(bot, ievent):
    if len(ievent.args) == 0:
        user = ievent.nick
    else:
        user = ' '.join(ievent.args)
    user_id = get_uid(bot, ievent, user)
    if not user_id:
        return
    bot.msg(choose_dest(ievent), '%s: http://egov4you.info/citizen/overview/%s' % (ievent.nick, user_id))

@expose('rankup')
def rankup(bot, ievent):
    rankings = {
        0: 'Recruit',
        15: 'Private',
        45: 'Private*',
        80: 'Private**',
        120: 'Private***',
        170: 'Corporal',
        250: 'Corporal*',
        350: 'Corporal**',
        450: 'Corporal***',
        600: 'Sergeant',
        800: 'Sergeant*',
        1000: 'Sergeant**',
        1400: 'Sergeant***',
        1850: 'Lieutenant',
        2350: 'Lieutenant*',
        3000: 'Lieutenant**',
        3750: 'Lieutenant***',
        5000: 'Captain',
        6500: 'Captain*',
        9000: 'Captain**',
        12000: 'Captain***',
        15500: 'Major',
        20000: 'Major*',
        25000: 'Major**',
        31000: 'Major***',
        40000: 'Commander',
        52000: 'Commander*',
        67000: 'Commander**',
        85000: 'Commander***',
        110000: 'Lt Colonel',
        140000: 'Lt Colonel*',
        180000: 'Lt Colonel**',
        225000: 'Lt Colonel***',
        285000: 'Colonel',
        355000: 'Colonel*',
        435000: 'Colonel**',
        540000: 'Colonel***',
        660000: 'General',
        800000: 'General*',
        950000: 'General**',
        1140000: 'General***',
        1350000: 'Field Marshal',
        1600000: 'Field Marshal*',
        1875000: 'Field Marshal**',
        2185000: 'Field Marshal***',
        2550000: 'Supreme Marshal',
        3000000: 'Supreme Marshal*',
        3500000: 'Supreme Marshal**',
        4150000: 'Supreme Marshal***',
        4900000: 'National Force',
        5800000: 'National Force*',
        7000000: 'National Force**',
        9000000: 'National Force***',
        11500000: 'World Class Force',
        14500000: 'World Class Force*',
        18000000: 'World Class Force**',
        22000000: 'World Class Force***',
        26500000: 'Legendary Force',
        31500000: 'Legendary Force*',
        37000000: 'Legendary Force**',
        43000000: 'Legendary Force***',
        50000000: 'God of War',
        100000000: 'God of War*',
        200000000: 'God of War**',
        500000000: 'God of War***',
    }

    if len(ievent.args) == 0:
        user = ievent.nick
    else:
        user = ' '.join(ievent.args)
    user_id = get_uid(bot, ievent, user)
    if not user_id:
        return
    profile = request('citizen.profile', id=user_id)

    next_rank_inf = 0
    for inf in sorted(rankings.keys()):
        if inf >= profile['rank']['points']:
            next_rank_inf = inf
            break
    next_rank = rankings[next_rank_inf]
    req_inf = (next_rank_inf - profile['rank']['points']) * 10

    hit = int(profile['hit']) * 1.0
    hit_q0 = int(req_inf / hit)

    msg = 'Prossimo rank per %s: \x02%s\x0F :: Inf richiesta: %d :: Q0: \x02%s\x0F :: Q1: \x02%s\x0F :: Q2: \x02%s\x0F :: Q3: \x02%s\x0F :: Q4: \x02%s\x0F :: Q5: \x02%s\x0F :: Q6: \x02%s\x0F :: Q7: \x02%s\x0F' % \
        (profile['name'], next_rank, req_inf, hit_q0, int(hit_q0 / 1.2),
         int(hit_q0 / 1.4), int(hit_q0 / 1.6), int(hit_q0 / 1.8),
         int(hit_q0 / 2), int(hit_q0 / 2.2), int(hit_q0 / 3))

    bot.msg(choose_dest(ievent), msg)

## https://docs.google.com/document/pub?id=1WYgNCGj-TO0e0PJU4j_Pl9gjbgs70O5Glt3x-7XMg3A
