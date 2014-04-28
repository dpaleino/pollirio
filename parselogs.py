#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import time
from collections import defaultdict
from pprint import pprint

channels = ['ufficiali', 'accademia-ei', 'reclute-war', 'erep-war']

ufficiali = {
    'Aelagon': 'Aelagon',
    'Aelagon|AwAy': 'Aelagon',
    'Aelagon|BNC': 'Aelagon',
    'bic': 'bic',
    'bicAFK': 'bic',
    'BNeCtore': 'BNeCtore',
    'corvobianco': 'corvobianco',
    'Dadevee': 'Dadevee',
    'dapal': 'dapal',
    'dapal|afk': 'dapal',
    'dapal|cena': 'dapal',
    'Dark_afk': 'Dark_Thunder',
    'Dark_Busy': 'Dark_Thunder',
    'DEVILPIERO': 'DEVILPIERO',
    'dirk|afk': 'dirkfelpy89',
    'dirk|coffee': 'dirkfelpy89',
    'dirkfelpy89': 'dirkfelpy89',
    'Fragiopa': 'Fragiopa',
    'Fragiopa-AFK': 'Fragiopa',
    'Halex19': 'Halex19',
    'Halex|BNC': 'Halex19',
    'Halex|BUSY': 'Halex19',
    'IlMessaggero': 'MercuriusTheOne',
    'kimi89na': 'kimi89na',
    'kimi89na|Afk': 'kimi89na',
    'kimi89na|BNC': 'kimi89na',
    'kimi89na|busy': 'kimi89na',
    'kimi89na|study': 'kimi89na',
    'kimi89na|pappa': 'kimi89na',
    'Kimi|euei': 'Kimilla',
    'Kimilla': 'Kimilla',
    'Kimillodora': 'Kimilla',
    'Kimmodora': 'Kimilla',
    'matteotommasi': 'matteotommasi',
    'MercuriusTheOne': 'MercuriusTheOne',
    'nabbic': 'bic',
    'nikidellicolli': 'nikidellicolli',
    'yap13': 'yap13',
}

stats = defaultdict(dict)

def reversed_lines(file):
    "Generate the lines of file in reverse order."
    part = ''
    for block in reversed_blocks(file):
        for c in reversed(block):
            if c == '\n' and part:
                yield part[::-1]
                part = ''
            part += c
    if part: yield part[::-1]

def reversed_blocks(file, blocksize=4096):
    "Generate blocks of file's contents in reverse order."
    file.seek(0, os.SEEK_END)
    here = file.tell()
    while 0 < here:
        delta = min(blocksize, here)
        here -= delta
        file.seek(here, os.SEEK_SET)
        yield file.read(delta)

for ch in channels:
    for line in open('logs/%s.log' % ch, 'r').readlines():
        m = re.match('^\[([^\] ]+)[^\]]+\] <([^>]+)> .*', line)
        if m:
            date = m.group(1)
            nick = m.group(2)

            try:
                stats[ufficiali[nick]][ch] = date
            except KeyError as ex:
                pass

# Sanitize stats
for officer in stats:
    for ch in channels:
        if not stats[officer].has_key(ch):
            stats[officer][ch] = None

#pprint(dict(stats))

print """<html>
<head>
<title>Controllo frequenza Ufficiali</title>
</head>
<body>
<table border='1'>
<thead>
<caption>Ultimo aggiornamento: %s</caption>
<tr>
<th>Ufficiale</th>
<th>#Accademia-EI</th>
<th>#erep-war</th>
<th>#reclute-war</th>
<th>#ufficiali</th>
</tr>
</thead>
<tbody>""" % time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(time.time()))

for officer in sorted(stats.keys(), key=lambda x: x.lower()):
    print """<tr>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
</tr>""" % (
        officer,
        stats[officer]['accademia-ei'],
        stats[officer]['erep-war'],
        stats[officer]['reclute-war'],
        stats[officer]['ufficiali']
    )

print """</tbody>
</table>
</body>
</html>"""
