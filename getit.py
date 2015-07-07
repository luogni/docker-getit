#!/usr/bin/python

import os.path
import subprocess
import sys
import tempfile

TEMPFILES = []
WDAVURL = "http://127.0.0.1:8080/seafdav"
WDAVMOUNT = "/srv/seafdav"
INIPATH = os.path.join(WDAVMOUNT, "Self", "getit.ini")
LASTPATH = os.path.join(WDAVMOUNT, "Self", "lastindex.csv")


def save_data(output):
    (fo, f) = tempfile.mkstemp()
    os.write(fo, output)
    os.close(fo)
    os.chmod(f, 0644)
    TEMPFILES.append(f)
    return f


def init_data():
    clean_data()
    os.system("mount -t davfs %s %s" % (WDAVURL, WDAVMOUNT))
    os.system("chmod a+w %s" % INIPATH)


def clean_data():
    for f in TEMPFILES:
        os.unlink(f)
    os.system("umount %s" % WDAVMOUNT)


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
    init_data()
    output = subprocess.check_output("docker run --rm=true -v %s:/getit.ini luogni/getit parsesite" % (INIPATH), shell=True)
    print "Find wanted files from index"
    f = save_data(output)
    with open(LASTPATH, "wb") as fl:
        fl.write(output)
    output = subprocess.check_output("docker run --rm=true -v %s:/getit.ini -v %s:/getitlist.csv luogni/getit getcmds" % (INIPATH, f), shell=True)
    for l in output.split('\n'):
        l = l.strip()
        if not l:
            continue
        (dst, cmdtype, fkey, cmd) = l.split('|', 3)
        print "Getting", l
        if cmdtype == 'download':
            os.system("docker run -ti --rm=true -v /srv/plex/media/%s:/download luogni/getit-download %s" % (dst, cmd))
        elif cmdtype == 'irc':
            f = save_data(cmd)
            os.system("docker run -ti --rm=true -v %s:/getitcmd.txt -v /srv/plex/media/%s:/weemedia luogni/getit-irc -- -r \"/connect irc.oltreirc.net; /set xfer.file.auto_accept_files on; /set xfer.file.download_path /weemedia/; /set xfer.file.use_nick_in_filename off; /python load /home/weechat/wdl.py;\"" % (f, dst))
    print "Refresh Plex library"
    os.system("docker exec plex ./Plex\ Media\ Scanner --scan --refresh")
    clean_data()
