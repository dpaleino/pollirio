# -*- coding: utf-8 -*-

from pollirio.modules import expose
from pollirio.dbutils import *
from pollirio import choose_dest
from pollirio import conf
from erepublik import get_uid

def reclute_link(bot, ievent, link):
    if ievent.channel.lower() not in ['#reclute-war', '#accademia-ei', '#erep-war']:
        return

    bot.sendLine('WHO %s' % ievent.channel)
    modes = bot.userlist[ievent.channel.lower()][ievent.nick]
    if '~' in modes or \
      '&' in modes or \
      '@' in modes or \
      '%' in modes or \
      ievent.nick == 'dapal':
        if len(ievent.args):
            nick = ievent.args[0]
        else:
            nick = ievent.nick
        bot.msg(choose_dest(ievent), '%s: %s' % (nick, link))
    return

@expose('arruola')
def arruola(bot, ievent):
    reclute_link(bot, ievent, 'http://tinyurl.com/Arruolamento')

@expose('lavoro')
def lavoro(bot, ievent):
    reclute_link(bot, ievent, 'http://tinyurl.com/LavoroEI')

@expose('equip')
def equip(bot, ievent):
    reclute_link(bot, ievent, 'http://tinyurl.com/EI-equip040214')

@expose('equipform')
def equip_form(bot, ievent):
    reclute_link(bot, ievent, 'http://ei-manage.hanskalabs.net/equip/form')

@expose('guida')
def guida(bot, ievent):
#    if ievent.channel.lower() not in ['#reclute-war', '#accademia-ei', '#erep-war', '#ei-tech']:
#        return

    topics = [
        'organizzazione',
        'equip',
        'regole',
        'primipassi',
        'registrazione',
        'chat',
        'dovespostarsi',
        'do',
        'mercenari',
        'battaglie',
    ]
    nick = ievent.nick
    if len(ievent.args) == 0:
        bot.msg(
            choose_dest(ievent),
            '%s: guide disponibili: ' % nick + ', '.join(topics) + '.'
        )
        return

    if len(ievent.args) == 2:
        nick = ievent.args[1]

    topic = ievent.args[0]
    if topic not in topics:
        bot.msg(
            choose_dest(ievent),
            '%s: guida "%s" non disponibile.' % (nick, topic)
        )
    else:
        msg = ''
        if topic == 'organizzazione':
            title = 'Come è fatto: Esercito eItaliano'
            url = 'http://www.erepublik.com/it/article/2229405/1/20'
        elif topic == 'equip':
            title = 'Come è fatto: Equipaggiamento, rimborsi e finanziamenti'
            url = 'http://www.erepublik.com/it/article/2229877/1/20'
        elif topic == 'regole':
            title = 'Regole da rispettare'
            url = 'http://www.erepublik.com/it/article/2300007/1/20'
        elif topic == 'primipassi':
            title = 'Primi Passi nel gioco'
            url = 'http://www.erepublik.com/it/article/2300767/1/20'
        elif topic == 'registrazione':
            title = 'Registrazione in chat: Mibbit e Rizon'
            url = 'http://www.erepublik.com/it/article/2233887/1/20'
        elif topic == 'chat':
            title = 'Perché stare in chat?'
            url = 'http://www.erepublik.com/it/article/2265417/1/20'
        elif topic == 'dovespostarsi':
            title = 'Guerre dirette e RW: dove mi sposto?'
            url = 'http://www.erepublik.com/it/article/2269933/1/20'
        elif topic == 'do':
            title = 'Il Daily Order, l\'ordine militare giornaliero'
            url = 'http://www.erepublik.com/it/article/2271419/1/20'
        elif topic == 'mercenari':
            title = 'Un colpo di bazooka e un #mercenaries'
            url = 'http://www.erepublik.com/it/article/2280072/1/20'
        elif topic == 'battaglie':
            title = 'Battaglie'
            url = 'http://www.erepublik.com/it/article/2063750/1/20'

        bot.msg(
            choose_dest(ievent),
            '%s: \x02%s\x0F - %s' % (nick, title, url)
        )

@expose('profilo')
def ei_profilo(bot, ievent):
    if len(ievent.args) == 0:
        user = ievent.nick
    else:
        user = ' '.join(ievent.args)
    user_id = get_uid(bot, ievent, user)
    if not user_id:
        return
    bot.msg(choose_dest(ievent), '%s: http://ei-manage.hanskalabs.net/users/view/%s' % (ievent.nick, user_id))
