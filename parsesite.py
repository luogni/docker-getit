#!/usr/bin/python

import lxml.html
import lxml.etree
import requests
import csv
import re
import cStringIO
import ConfigParser
import xml.parsers.expat


# we can also use comments feed i think.. http://HOST/comments/feed/
URLS = [
    # {'u': 'http://www.hitecno.net/?paged=',
    #  'm': 'wordpress', 'c': '1 Comment', 'h': 'atenalist', 'add': 'completa/',
    #  'server': 'darksin', 'channel': 'atena'},
    # {'u': 'http://www.tecnoevolution.net/?paged=',
    #  'm': 'wordpress', 'c': '1 Comment', 'h': 'webuniversal', 'add': '/completa/',
    #  'server': 'darksin', 'channel': 'universal'},

    {'u': "http://www.altatechnology.net/?paged=",
     'cmdtype': 'irc', 'wantsections': False,
     'm': 'wordpress', 'c': '1 Comment', 'h': 'maleficent', 'add': '/completa/'},
    {'u': 'http://serietvsubita.net/category/%s/feed/',
     'cmdtype': 'download', 'wantsections': True,
     'm': 'blog'}
]


def unescape(s):
    want_unicode = False
    if isinstance(s, unicode):
        s = s.encode("utf-8")
        want_unicode = True

    # the rest of this assumes that `s` is UTF-8
    list = []

    # create and initialize a parser object
    p = xml.parsers.expat.ParserCreate("utf-8")
    p.buffer_text = True
    p.returns_unicode = want_unicode
    p.CharacterDataHandler = list.append

    # parse the data wrapped in a dummy element
    # (needed so the "document" is well-formed)
    p.Parse("<e>", 0)
    p.Parse(s, 0)
    p.Parse("</e>", 1)

    # join the extracted strings and return
    es = ""
    if want_unicode:
        es = u""
    return es.join(list)


def find_url(urls, sections):
    rets = []
    for u in URLS:
        cmdtype = u['cmdtype']
        ws = u['wantsections']
        ss = sections
        if not ws:
            ss = [None]
        for s in ss:
            ret = PL[cmdtype]['find'](u, s)
            if ret:
                rets.append({'cmdtype': cmdtype, 'data': ret, 'section': s})
    return rets


def parse_index(data, files):
    cmdtype = data['cmdtype']
    return PL[cmdtype]['parse'](data, files)


def gotit(files, k, cmd, data):
    files[str(k)] = {'cmd': cmd, 'cmdtype': data['cmdtype'], 'section': data['section']}


# IRC #
def find_url_irc(u, section):
    for i in range(1, 5):
        url = u['u'] + str(i)
        if u['m'] == 'wordpress':
            ret = find_url_wordpress(url, u)
            if ret:
                return ret
    return None


def find_url_wordpress(url, params):
    try:
        p = lxml.html.parse(url).getroot()
    except:
        return
    for c in p.cssselect('a'):
        try:
            con = str(c.text_content()).strip()
        except:
            continue
        if con == params['c']:
            p = lxml.html.parse(c.get('href')).getroot()
            for c in p.cssselect('a'):
                if c.get('href').find(params['h']) >= 0:
                    u = c.get('href') + params['add']
                    r = requests.get(u)
                    return r.content
    return None


def parse_index_irc(data, files):
    d = data['data']
    for a in re.findall('align=left> (.+?) </td>.+?(msg .+? xdcc send #\d+?) ', d):
        (f, cmd) = a
        if f.endswith('.avi') or f.endswith('.mp4'):
            gotit(files, f, "/" + cmd, data)
    return files
# END IRC


# BLOG
def find_url_blog(u, section):
    url = u['u'] % section
    try:
        r = requests.get(url)
    except:
        return None
    return r.content


def parse_index_blog(data, files):
    d = data['data']
    section = data['section']
    root = lxml.etree.fromstring(d)
    sep = []
    for el in root.iter():
        if el.tag == 'title':
            t = el.text
            for r in [('(S\d\dE\d\d)')]:
                aa = re.findall(r, t)
                sep = aa
        elif el.tag == 'description':
            t = unescape(el.text).strip()
            for s in sep:
                e = s[-2:]
                RE = [
                    (':: Episodio %s .(.+?). ::.+? (http://www.videowood.tv/video/.+?)$' % e),
                    (':: Episodio %s .(.+?). ::.+? (http://www.videowood.tv/video/.+?) ' % e)
                    # (':: Episodio (\d+) .(.+?). ::.+? (http://vidto.me/.+?\.html) ')]
                ]
                for r in RE:
                    aa = re.findall(r, t)
                    if aa:
                        (title, dl) = aa[0]
                        title = "".join([c for c in title if ((ord(c) > 31)and(ord(c) < 126))or(ord(c) == 9)])
                        k = "%s.%s.mp4" % (section, s)
                        gotit(files, k, dl, data)
    return files

# END BLOG


PL = {'irc': {'find': find_url_irc,
              'parse': parse_index_irc},
      'download': {'find': find_url_blog,
                   'parse': parse_index_blog}
      }


def main():
    config = ConfigParser.RawConfigParser()
    config.read(['/getit.ini', 'getit.ini'])
    sections = config.sections()
    data = find_url(URLS, sections)
    files = {}
    for d in data:
        files = parse_index(d, files)
    if files:
        ss = cStringIO.StringIO()
        c = csv.writer(ss)
        for k in sorted(files.keys()):
            f = files[k]
            c.writerow([k, f['cmdtype'], f['cmd']])
        print ss.getvalue().strip()

if __name__ == '__main__':
    main()
