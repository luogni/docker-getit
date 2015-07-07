#!/usr/bin/python

import csv
import ConfigParser
import re

TODO = -2  # used for movies
DONE = -1


def output_cmd(config, dls, k, where, cmd, e, name, cmdtype):
    dls[k] = e
    config.set(k, "last", e)
    print "%s|%s|%s|%s" % (where, cmdtype, name, cmd)


def parse_episode(name):
    for r in ["\.S(\d\d)E(\d\d)\."]:
        ret = re.findall(r, name)
        if ret:
            (s, e) = ret[0]
            return int(s) * 100 + int(e)


config = ConfigParser.RawConfigParser()
configname = config.read(['/getit.ini', 'getit.ini'])[0]


dls = {}
for s in config.sections():
    try:
        l = config.getint(s, "last")
    except:
        l = TODO
    dls[s] = l

keys = dls.keys()

# csv is ordered so also episodes are ordered
with open("/getitlist.csv") as f:
    c = csv.reader(f)
    for line in c:
        try:
            (name, cmdtype, cmd) = line
        except:
            continue
        done = []
        for k in keys:
            if name.startswith(k):
                if (dls[k] >= 0):
                    e = parse_episode(name)
                    if (e is not None)and(e > dls[k]):
                        output_cmd(config, dls, k, "TvShows", cmd, e, name, cmdtype)
                elif (dls[k] == TODO):
                    output_cmd(config, dls, k, "Movies", cmd, DONE, name, cmdtype)

with open(configname, 'wb') as f:
    config.write(f)
