from __future__ import print_function
import urllib

f = open('imgs', 'w')
url = "http://img1.jurko.net/%s.gif"
for x in range(1, 99999):
    res = urllib.urlopen(url % x)
    if res.info().type == 'image/gif':                        
        f.write('|%s' % (url % x))


