# -*- coding: utf-8 -*-

from pollirio.modules import expose
from pollirio.dbutils import *
from pollirio import choose_dest
from pollirio import conf

import cjson as json
from datetime import datetime
from requests import session
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
import hashlib
import hmac
import locale
from lxml.html.soupparser import fromstring
from pprint import pprint

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

private = conf.config.get('erepublik', 'api_private')
public = conf.config.get('erepublik', 'api_public')
username = conf.config.get('erepublik', 'username')
password = conf.config.get('erepublik', 'password')

locale.setlocale(locale.LC_ALL, 'C')

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
        1000000000: 'Titan',
        2000000000: 'Titan*',
        4000000000: 'Titan**',
        10000000000: 'Titan***',
    }

def login():
    payload = dict(
        citizen_email = username,
        citizen_password = password,
        remember = 'on',
    )

    s = session()
    s.post('http://www.erepublik.com/en/login', data=payload)
    return s

def request(resource, action, **args):
    #oldlocale = locale.getlocale()
    #locale.setlocale(locale.LC_ALL, 'C')

    date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S')
    params = None
    if args:
        params = urlencode(args).lower()

    query = ':'.join([x for x in [resource, action, params, date] if x is not None])
    auth = hmac.new(private, query, hashlib.sha256).hexdigest()

    s = session()
    headers = {
        'Date': date,
        'Auth': '%s/%s' % (public, auth),
    }
    page = s.get('http://api.erepublik.com/citizen/profile', params=args, headers=headers)
    pprint(json.decode(page.text))
    return json.decode(page.text)['message']

def scrape(resource, **args):
    session = login()

    if resource == 'uid':
        # we effectively only need the first user, so don't scrape all pages
        search = session.get(
            'http://www.erepublik.com/en/main/search/%s/' %
                args['query'].replace(' ', '_')
        )
        doc = fromstring(search.text)
        uid = doc.xpath('//div[@class="nameholder"]/a/@href')[0].split('/')[-1].strip()
        return uid

    #patterns = {
        #'citizen.profile': 'citizen/profile/%(id)d',
        #'citizen.search': 'citizen/search/%(query)s/%(page)d',
        #'battle.active': 'battle/active',
        #'battle': 'battle/%(id)d',
        #'country.society': 'country/%(country)s/society',
        #'country.economy': 'country/%(country)s/economy',
        #'party': 'party/%(id)d',
        #'mu': 'mu/%(id)d',
        #'mu.regiment': 'mu/%(id)d/%(regiment)d',
        #'market': 'market/%(country)s/%(industry)s/%(quality)d/%(page)d',
        #'job.market': 'jobmarket/%(country)s/%(page)d',
        #'exchange': 'exchange/%(mode)d/%(page)d',
        #'election.president': 'election/president/%(year)d/%(month)d/%(country)s',
        #'election.congress': 'election/congress/%(year)d/%(month)d/%(country)s/%(region)s',
        #'election.party': 'election/congress/%(year)d/%(month)d/%(country)s/%(party)d',

def get_uid(bot, ievent, user):
    ret = users.search(user)
    if ret:
        return int(ret[0][2])
    uid = scrape('uid', query=user)
    if uid:
        users.add(user, uid)
        return uid
    else:
        bot.msg(choose_dest(ievent), '%s: utente «%s» non trovato.' % (ievent.nick, user))
        return None

def get_hit(strength, rank_points):
    level = 0
    for points in sorted(list(rankings.keys())):
        if points > int(rank_points):
            break
        level += 1
    base_hit = 10 * (1 + float(strength) / 400.0) * (1 + level / 5.0)
    return int(round(base_hit))

@expose('lp')
def list_profile(bot, ievent):
    if len(ievent.args) == 0:
        user = ievent.nick
    else:
        user = ' '.join(ievent.args)
    user_id = get_uid(bot, ievent, user)
    if not user_id:
        return
    profile = request('citizen', 'profile', citizenId=user_id)
    age = datetime.now() - datetime.strptime(profile['general']['birthDay'], '%b %d, %Y')

    if not profile['party']:
        profile['party'] = {'name': 'Nessun partito'}
    if not profile['militaryUnit']:
        profile['militaryUnit'] = {'name': 'Nessuna MU'}

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
            profile['general']['level'],
            age.days,
            profile['general']['experience_points'],
            profile['militaryAttributes']['strength'],
            profile['militaryAttributes']['rank_name'] + '*'*profile['militaryAttributes']['rank_stars'],
            profile['militaryAttributes']['rank_points'],
            profile['general']['nationalRank'],
            profile['location']['citizenship_country_initials'],
            profile['location']['residence_country_name'],
            profile['location']['residence_region_name'],
            profile['party']['name'],
            profile['militaryUnit']['name']
        )
    )

@expose('fc')
def fight_calc(bot, ievent):
    #bot.msg(choose_dest(ievent), '%s: .fc non è al momento disponibile.' % ievent.nick)
    if len(ievent.args) == 0:
        user = ievent.nick
    else:
        user = ' '.join(ievent.args)
    user_id = get_uid(bot, ievent, user)
    if not user_id:
        return
    profile = request('citizen', 'profile', citizenId=user_id)
    hit = get_hit(profile['militaryAttributes']['strength'], profile['militaryAttributes']['rank_points'])
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
def donate(bot, ievent):
    if len(ievent.args) == 0:
        user = ievent.nick
    else:
        user = ' '.join(ievent.args)
    user_id = get_uid(bot, ievent, user)
    if not user_id:
        return
    bot.msg(choose_dest(ievent), '%s: http://www.erepublik.com/en/economy/donate-items/%s' % (ievent.nick, user_id))

@expose('money')
def money(bot, ievent):
    if len(ievent.args) == 0:
        user = ievent.nick
    else:
        user = ' '.join(ievent.args)
    user_id = get_uid(bot, ievent, user)
    if not user_id:
        return
    bot.msg(choose_dest(ievent), '%s: http://www.erepublik.com/en/economy/donate-money/%s' % (ievent.nick, user_id))

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
    if len(ievent.args) == 0:
        user = ievent.nick
    else:
        user = ' '.join(ievent.args)
    user_id = get_uid(bot, ievent, user)
    if not user_id:
        return
    profile = request('citizen', 'profile', citizenId=user_id)

    next_rank_inf = 0
    for inf in sorted(rankings.keys()):
        if inf >= int(profile['militaryAttributes']['rank_points']):
            next_rank_inf = inf
            break
    next_rank = rankings[next_rank_inf]
    req_inf = (next_rank_inf - int(profile['militaryAttributes']['rank_points'])) * 10

    hit = get_hit(profile['militaryAttributes']['strength'], profile['militaryAttributes']['rank_points'])
    hit_q0 = int(req_inf / hit)
    hit_q0 = 0

    msg = 'Prossimo rank per %s: \x02%s\x0F :: Inf richiesta: %d :: Q0: \x02%s\x0F :: Q1: \x02%s\x0F :: Q2: \x02%s\x0F :: Q3: \x02%s\x0F :: Q4: \x02%s\x0F :: Q5: \x02%s\x0F :: Q6: \x02%s\x0F :: Q7: \x02%s\x0F' % \
        (profile['general']['name'], next_rank, req_inf, hit_q0, int(hit_q0 / 1.2),
         int(hit_q0 / 1.4), int(hit_q0 / 1.6), int(hit_q0 / 1.8),
         int(hit_q0 / 2), int(hit_q0 / 2.2), int(hit_q0 / 3))

    bot.msg(choose_dest(ievent), msg)

@expose('party', 1)
def party(bot, ievent):
    '''party <abbreviazione partito>'''
    bot.msg(choose_dest(ievent), '%s: .party non è al momento disponibile.' % ievent.nick)
    #party = ievent.args[0]
    #parties = {
        #'ler': 4010,
        #'letr': 4010,
        #'fdi': 4147,
        #'fdei': 4147,
        #'pce': 872,
        #'rei': 3878,
        #'aetg': 641,
        #'lgei': 2540,
        #'pdl': 4287,
        #'bastardi': 3088,
        #'bsg': 3088,
        #'lei': 2191,
        #'ieso': 3060,
        #'puv': 3166,
        #'movimento': 2360,
        #'pmi': 2687,
        #'api': 4276,
        #'pdl': 4287,
    #}
    #party_id = parties[party]
    #party = request('party', id=party_id)
    #bot.msg(
        #choose_dest(ievent),
        #'\x02Nome partito:\x0F %s ' \
        #'\x02Membri:\x0F %s ' \
        #'\x02PP:\x0F %s ' \
        #'\x02CM:\x0F %d' %
        #(
            #party['name'],
            #party['members'],
            #party['president']['name'],
            #party['congress']['members']
        #)
    #)

## https://docs.google.com/document/pub?id=1WYgNCGj-TO0e0PJU4j_Pl9gjbgs70O5Glt3x-7XMg3A
