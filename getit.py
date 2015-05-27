#!/usr/bin/python

import os
import subprocess
import sys
import tempfile

TEMPFILES = []


def save_data(output):
    (fo, f) = tempfile.mkstemp()
    os.write(fo, output)
    os.close(fo)
    os.chmod(f, 0644)
    TEMPFILES.append(f)
    return f


def clean_data():
    for f in TEMPFILES:
        os.unlink(f)


try:
    mode = sys.argv[1]
except:
    mode = "master"

if mode == "parsesite":
    os.system("/home/getit/parsesite.py")

elif mode == "getcmds":
    os.system("/home/getit/getcmds.py")

elif mode == "master":
    print "Get and parse index"
    output = subprocess.check_output("docker run --rm=true luogni/getit parsesite", shell=True)
    print "Find wanted files from index"
    f = save_data(output)
    with open("/root/lastindex.csv", "wb") as fl:
        fl.write(output)
    output = subprocess.check_output("docker run --rm=true -v /srv/getit.ini:/getit.ini -v %s:/getitlist.csv luogni/getit getcmds" % f, shell=True)
    for l in output.split('\n'):
        l = l.strip()
        if not l:
            continue
        (dst, cmd) = l.split('|', 1)
        print "Getting", l
        f = save_data(cmd)
        os.system("docker run -ti --rm=true -v %s:/getitcmd.txt -v /srv/plex/media/%s:/weemedia luogni/getit-irc -- -r \"/connect irc.oltreirc.net; /set xfer.file.auto_accept_files on; /set xfer.file.download_path /weemedia/; /set xfer.file.use_nick_in_filename off; /python load /home/weechat/wdl.py;\"" % (f, dst))
    print "Refresh Plex library"
    os.system("docker exec plex ./Plex\ Media\ Scanner --scan --refresh")
    clean_data()
