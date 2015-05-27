import lxml.html
import sys
import requests
import csv
import re


URLS = ["http://www.altatechnology.net/",
        "http://www.altatechnology.net/?paged=2"]


def find_url_wordpress(urls):
    for u in urls:
        p = lxml.html.parse(u).getroot()
        for c in p.cssselect('a'):
            try:
                con = str(c.text_content()).strip()
            except:
                continue
            if con == '1 Comment':
                p = lxml.html.parse(c.get('href')).getroot()
                for c in p.cssselect('a'):
                    if c.get('href').find('maleficent') >= 0:
                        print "URL", c.get('href')
                        r = requests.get(c.get('href') + '/completa')
                        return r.content
    return None


def parse_index(data):
    files = {}
    for a in re.findall('align=left> (.+?) </td>.+?(msg .+? xdcc send #\d+?) ', data):
        (f, cmd) = a
        if f.endswith('.avi') or f.endswith('.mp4'):
            files[f] = "/" + cmd
    return files


def main():
    destfile = sys.argv[1]
    data = find_url_wordpress(URLS)
    if data:
        files = parse_index(data)
        if files:
            with open(destfile, "wb") as f:
                c = csv.writer(f)
                for k in sorted(files.keys()):
                    c.writerow([k, files[k]])

if __name__ == '__main__':
    main()
