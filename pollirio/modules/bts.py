# -*- coding: utf-8 -*-

#from pollirio.irc_colours import colourise
from pollirio.modules import expose

from btsutils.debbugs import debbugs
from urllib import urlencode
from urllib2 import urlopen, HTTPError
from BeautifulSoup import BeautifulSoup

# Synced from dak:config/debian/pseudo-packages.description
pseudo_packages = {
    'base': 'Base system general bugs',
    'cdrom': 'Installation system',
    'spam': 'Spam (reassign spam to here so we can complain about it)',
    'press': 'Press release issues',
    'kernel': 'Problems with the Linux kernel, or that shipped with Debian',
    'project': 'Problems related to project administration',
    'general': 'General problems (e.g. "many manpages are mode 755")',
    'buildd.debian.org': 'Buildd maintainers',
    'nm.debian.org': 'New Maintainer process and nm.debian.org webpages',
    'qa.debian.org': 'The Quality Assurance group',
    'ftp.debian.org': 'Problems with the FTP site',
    'www.debian.org': 'Problems with the WWW site',
    'bugs.debian.org': 'The bug tracking system, @bugs.debian.org',
    'lists.debian.org': 'The mailing lists, debian-*@lists.debian.org',
    'wnpp': 'Work-Needing and Prospective Packages list',
    'cdimage.debian.org': 'CD Image issues',
    'tech-ctte': 'The Debian Technical Committee (see the Constitution)',
    'mirrors': 'Problems with the official mirrors',
    'security.debian.org': 'The Debian Security Team',
    'installation-reports': 'Reports of installation problems with stable & testing',
    'upgrade-reports': 'Reports of upgrade problems for stable & testing',
    'release-notes': 'Problems with the Release Notes',
    'wiki.debian.org': 'Problems with the Debian wiki',
    'security-tracker': 'The Debian Security Bug Tracker',
    'release.debian.org': 'Requests regarding Debian releases and release team tools',
    'listarchives': 'Problems with the WWW mailing list archives',
}

@expose("bug", 1)
def bug(bot, ievent):
    """bug <bugid>"""
    bts = debbugs()
    b = bts.get(int(ievent.args[0]))

    status = "(fixed) " if b.status == "done" else ""
    severity = "(%s) " % b.severity if b.severity != "normal" else ""

    #msg = colourise("[bug]#%s[reset]%s: %s: «[title]%s[reset]»%s [url]%s[reset]" % (b.bug, status, package, b.summary, severity, b.url)).decode("utf-8")
    #msg = "#%s%s: %s: %s%s %s" % (b.bug, status, b.package, b.summary, severity, b.url)
    msg = "%s %s%s- %s: %s" % (b.url, status, severity, b.package, b.summary)
    bot.msg(ievent, "%s: %s" % (ievent.nick, msg.encode("utf-8")))

@expose("qa", 1)
def qa(bot, ievent):
    """qa <package>"""
    package = str(ievent.args[0])

    if package.startswith("lib"):
        prefix = package[:4]
    else:
        prefix = package[:1]

    try:
        url = "http://packages.qa.debian.org/%s/%s.html" % (prefix, package)
        f = urlopen(url)
        msg = "%s: %s" % (ievent.nick, url)
    except HTTPError, e:
        if e.code == 404:
            msg = "%s: package %s does not exist" % (ievent.nick, package)
        else:
            msg = "%s: %s" % (ievent.nick, e.msg)

    bot.msg(ievent, msg.encode("utf-8"))

@expose("maintainer", 1)
def maintainer(bot, ievent):
    """maintainer <package>"""
    package = str(ievent.args[0])

    if package.startswith("lib"):
        prefix = package[:4]
    else:
        prefix = package[:1]

    try:
        url = "http://packages.qa.debian.org/%s/%s.html" % (prefix, package)
        f = urlopen(url)
    except HTTPError, e:
        if e.code == 404:
            msg = "%s: package %s does not exist" % (ievent.nick, package)
        else:
            msg = "%s: %s" % (ievent.nick, e.msg)
        bot.msg(ievent, msg.encode("utf-8"))
        return

    msg = "%s: maintainer for %s is " % (ievent.nick, package)
    soup = BeautifulSoup(f)
    maint = soup.find('span', {'title':'maintainer'})
    email = maint.parent['href'].split('login=')[1]
    msg += "%s <%s>" % (maint.string, email)
    uploaders = soup.findChildren('span', {'title':'uploader'})
    if uploaders:
        msg += ", uploaders: "
        tmp = []
        for u in uploaders:
            tmp.append("%s <%s>" % (u.string, u.parent['href'].split('login=')[1]))
        msg += ', '.join(tmp)
    bot.msg(ievent, msg.encode("utf-8"))

@expose("madison", 1)
def madison(bot, ievent):
    """madison <package> [package, package, ...]"""
    package = str(ievent.args[0])
    if len(ievent.args) > 1:
        suites = ",".join(ievent.args[1:])
    else:
        suites = ""

    data = urlencode({
        'package': package,
        's': suites,
        'text': 'on',
        })

    f = urlopen('http://qa.debian.org/madison.php?%s' % data)
    for l in f.readlines():
        bot.msg(ievent, "%s: %s" % (ievent.nick, l.rstrip().encode("utf-8")))

@expose("popcon", 1)
def popcon(bot, ievent):
    """popcon <package>"""
    package = str(ievent.args[0])
    data = urlencode({'package': package})

    try:
        f = urlopen("http://qa.debian.org/popcon.php", data)
    except HTTPError, e:
        if e.code == 404:
            msg = "%s: package %s does not exist" % (ievent.nick, package)
        else:
            msg = "%s: %s" % (ievent.nick, e.msg)
        bot.msg(ievent, msg.encode("utf-8"))
        return

    soup = BeautifulSoup(f)
    rows = [x.string for x in soup('td')[1:]]
    fields = {
        'inst': int(rows[0]),
        'vote': int(rows[3]),
        'old': int(rows[6]),
        'recent': int(rows[9]),
        'nofiles': int(rows[12]),
    }

    msg  = "%s: popcon for %s - " % (ievent.nick, package)
    for f in fields:
        msg += "%s: %d " % (f, fields[f])
    msg += "- http://qa.debian.org/developer.php?popcon=%s" % package
    bot.msg(ievent, msg.encode("utf-8"))
