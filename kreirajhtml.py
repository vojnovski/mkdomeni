#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import datetime
import sqlite3
import pickle
from bs4 import BeautifulSoup
import codecs
import cgi
import urllib2,urllib,pickle
import re

def novi_domejni(datumnov):
    """��� ������� �� ��� �� datumnov � �� ���� �� datumstar."""

    conn = sqlite3.connect("domaininfo.sqlite3")
    c = conn.cursor()
    
    c.execute("""
            select 
                domen 
            from 
                domaininfo 
            where 
                date=?
                and status = 'Y'""",
            (datumnov.strftime("%Y-%m-%d")))

   # a = [(novdomejn[0],novdomejn[1]) for novdomejn in c]

   # c.execute("select count(*) from novidomejni where datum=?",(datumstar.strftime("%Y-%m-%d"),))
   # if c.fetchone()[0]==    0:
   #     c.execute("insert into novidomejni values (?,?)",(datumstar.strftime("%Y-%m-%d"),len(a)))
   #     conn.commit()

    c.close()
    return c

def format_date(dt):
    """convert a datetime into an RFC 822 formatted date

        Input date must be in GMT.
    """
    # Looks like:
    #   Sat, 07 Sep 2002 00:00:01 GMT
    # Can't use strftime because that's locale dependent
    #
    # Isn't there a standard way to do this for Python?  The
    # rfc822 and email.Utils modules assume a timestamp.  The
    # following is based on the rfc822 module.
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (
                ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()],
                dt.day,
                ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][dt.month-1],
                dt.year, dt.hour, dt.minute, dt.second)

def output_html(novidomejni):
    if not novidomejni:
        return

    import grafici
    podatum_grafik = grafici.novidomejni_grafik()
    potip_grafik = grafici.tipovidomejn_grafik()

    fajl = codecs.open("index.html","w","utf-8")
    fajl.write(u"""<html>
        <head>
        <title>���� ������������ ������� �������</title>
        <meta http-equiv="content-type" content="text/html; charset=utf-8">
        <meta name="Author" content="Georgi Stanojevski <http://isengard.unet.com.mk/~georgi/ueb/>">
        <link rel="shortcut icon" href="favicon.ico" />
        <link rel="alternate" type="application/rss+xml" title="������� �������" href="/novidomejni.xml" />
        <style>
            body { 
            font-family: sans-serif;
            }
        </style>
    </head><body>
    <p>&nbsp;</p>
    <p><b>��������� �� �� <a href='/novidomejni.xml'>RSS �������</a> �� ������ �� �������� ��� �� ���o ������������ .mk �������.</b></p>
    <p>���� ������������ �������:</p>""")

    fajl.write(u"<ul>")
    for element in novidomejni:
        fajl.write(u"<li><a title='���� �� ������' href='http://dns.marnet.net.mk/registar.php?dom=%s'>%s</a> (<a href='http://www.%s' title='��� ������'><img border=0 src='/external.png' /></a>)</li>" % (element[1],element[1],element[1]))

    fajl.write(u"</ul>")

    fajl.write(u'<center><img src="%s" alt="Novi domejni poslednite 30 denovi" /></center><br /><br /><br />' % podatum_grafik)
    fajl.write(u'<center><img src="%s" alt="Registrirani .mk domeni po tip" /></center><br /><hr />' % potip_grafik)
    fajl.write(u'<p>�������� � <a href="/podatum/">����</a>, ��������� �� ��� �� �������� <a href="/novimkdomejni.tar.gz">����</a>, �������� ������ �� <a href="http://isengard.unet.com.mk/~georgi/ueb/">http://isengard.unet.com.mk/~georgi/ueb/</a></p></body></html>')


def output_rss(novidomejni):
    """RSS �� ������. ��� ���� ���� �� �� ����� ������� ���."""
    if not novidomejni:
        return


    fajl = codecs.open("novidomejni.xml","w","utf-8")
    fajl.write(u"""<?xml version="1.0" encoding="utf-8"?>
                        <rss version="2.0">
                        <channel>
                        <title>���� .�� �������</title>
                        <link>http://domejn.ot.mk</link>
                        <description>����� �� ���� �������������� ������� �������.</description>
                        <language>mk</language>
                        <image>
                        <title>���� .�� �������</title>
                        <url>mk.jpg</url>
                        <link>http://domejn.ot.mk</link>
                        </image>\n""")

    for element in novidomejni:
        fajl.write("""<item>
                            <title>%s</title>
                            <link>http://dns.marnet.net.mk/registar.php?dom=%s</link>
                            <description>&lt;a href=&quot;http://www.%s&quot;&gt;%s&lt;/&gt;</description>
                            <pubDate>%s</pubDate>
                            <guid>http://dns.marnet.net.mk/registar.php?dom=%s</guid>
                            </item>""" % 
                (element[1],
                element[1],
                element[1],
                element[1],
                format_date(datetime.datetime.strptime(element[0],'%Y-%m-%d')),
                element[1]))

    fajl.write("</channel></rss>")
    fajl.close()



if __name__=="__main__":
    pass
    #novi = novi_domejni(datetime.datetime.now().date())
       # if novi:
        #    import shutil
         #   shutil.copyfile("index.html","%s.html" % datumstar.strftime("%Y%m%d"))
          #  output_rss(novi)
           # output_html(novi)
