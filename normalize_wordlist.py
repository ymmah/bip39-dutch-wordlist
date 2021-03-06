# -*- coding: utf-8 -*-
#
#    bip39-dutch-wordlist - Normalize List
#    Copyright (C) 2016 October 
#    1200 Web Development
#    http://1200wd.com/
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import re
from wordfreq import wordfreq
from wordtype import wordtype

DICTFILES = [
    {
        'file': 'data/SONAR500.lemmaposfreqlist.1-gram.total.top5000.tsv',
        'struct': ['word','type','frequency'],
        'allowed-types': ['WW','N','ADJ'],
        'priority': 1,
    },
    {
        'file': 'data/dutch-wordlist.txt',
        'struct': ['word'],
        'priority': 2,
    },
]
ALLOWED_CHARS = 'abcdefghijklmnopqrstuvwxyz'
OUTPUTFILE = 'data/dutch-norm.txt'
MINFREQ = 4

workdir = os.path.dirname(__file__)


def create_normalized():
    global workdir
    rebrackets = re.compile(".*?\((.*?)\)")
    normdict = []
    wordcount = 0
    for dictio in DICTFILES:
        dictfile = dictio['file']
        print("Reading and parsing %s" % dictfile)
        with open('%s/%s' % (workdir, dictfile), 'rb') as f:
            wordlist = [w.strip() for w in f.readlines()]
        print("Found %d words" % len(wordlist))
        for line in wordlist:
            wordcount += 1
            fields = line.split()
            data = {}
            i = 0
            for fld in dictio['struct']:
                fieldval = fields[i]
                try:
                    fieldval = fieldval.decode('utf-8')
                except:
                    print("Error decoding %s" % fieldval)
                    break
                if fld == 'word':
                    fieldval = fieldval.strip('\r\n')
                    if len(fieldval) < 3 or len(fieldval) > 8:
                        data = {}
                        break
                    fieldval = fieldval.lower()
                    foundstrangechar = False
                    for char in fieldval:
                        if char not in ALLOWED_CHARS:
                            foundstrangechar = True
                    if foundstrangechar:
                        data = {}
                        break
                elif fld == 'type':
                    typecom = re.findall(rebrackets, fieldval)[0]
                    fieldval = fieldval.replace("(" + typecom + ")","")
                    if fieldval not in dictio['allowed-types']:
                        data = {}
                        break
                if fieldval:
                    data.update({
                        fld: fieldval
                    })
                    i += 1

            if data:
                if not data['word'] in [nd['word'] for nd in normdict]:
                    if 'freqency' not in data:
                        if data['word'] not in wordfreq or wordfreq[data['word']] < MINFREQ:
                            continue
                        else:
                            data['frequency'] = wordfreq[data['word']]
                    if 'type' not in data:
                        nt = ''
                        if data['word'] in wordtype:
                            t = wordtype[data['word']]
                            if 'Z' in t or 'C' or 'Yb' in t:
                                nt = 'N'
                            elif 'Vi' in t:
                                nt = 'WW'
                            elif 'Aa' in t or 'Ab' in t:
                                nt = 'ADJ'
                        data['type'] = nt
                    if data:
                        data.update({'priority': dictio['priority']})
                        normdict.append(data)
        print("%d words accepted sofar" % len(normdict))

    return sorted(normdict, key=lambda k: k['word'])


if __name__ == '__main__':
    wordlist = create_normalized()
    print("%d word are added to normalized wordlist" % len(wordlist))

    with open('%s/%s' % (workdir, OUTPUTFILE), 'w') as f:
        for wl in wordlist:
            line = "%s,%s,%d,%d\n" % (wl['word'], wl['type'], wl['priority'], wl['frequency'])
            f.write(line)
