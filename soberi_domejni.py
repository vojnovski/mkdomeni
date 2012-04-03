#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

#import sqlite3 #GAEquirk
import re
import pickle
import logging
import datetime
import urllib2,urllib,pickle
from BeautifulSoup import BeautifulSoup
from google.appengine.api import rdbms
from google.appengine.api import urlfetch
from google.appengine.api import urlfetch_errors
from google.appengine.runtime import apiproxy_errors 


format_na_datum="%d-%m-%Y"
deneska = datetime.datetime.now().date()
_INSTANCE_NAME = 'mkdomainssql:mkdomainsql'
gae = True;

def stranici():
    """Букви на http://dns.marnet.net.mk/registar.php"""
    bukvi = ['NUM','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

    url = 'http://dns.marnet.net.mk/registar.php'

    linkovi = []
    for bukva in bukvi:
        logging.info(u"Proveruvam Bukva %s" % bukva)
        bukva = urllib.urlencode({'bukva':bukva})
        req = urllib2.Request(url,bukva)
        res = urllib2.urlopen(req)

        stranica = res.read()

        soup = BeautifulSoup(stranica)
        rawlinkovi = soup.findChildren('a',{'class':'do'})
        
        for link in rawlinkovi:
            if link['href'].find('del=') <> -1:
                linkovi.append(link['href'])

    return linkovi

def zemi_domejni(stranici):
    """Ги зима домејните од Марнет. stranici треба да е ажурна
    листа на страници од главната страница на Марнет."""

    #ako deneska sum sobral ne probuvaj pak
    if gae:
        conn = rdbms.connect(instance=_INSTANCE_NAME, database='domaininfo')
    else:
        pass
        #conn = sqlite3.connect("db/domaininfo.sqlite3") #GAEquirk
    c = conn.cursor()
    c.execute('select count(*) from domaininfo where date=%s',(deneska,))
    if c.fetchone()[0]<>0:
        return []

    domejni = []
    for link in stranici:
        logging.info(u"Sobiram %s" % link)

        req = urllib2.Request(u'http://dns.marnet.net.mk/' + link)
        res = urllib2.urlopen(req)
        strana = res.read()
        soup = BeautifulSoup(strana)

        domejn_linkovi = soup.findChildren('a',{'class':'do'})

        for domejn in domejn_linkovi:
            if domejn['href'].find('dom=')<>-1:
                domejni.append(domejn['href'].replace('registar.php?dom=',''))

    return domejni
    
    
def dodaj_domejn(domejn,conn):
    
    logging.info(u"Dodavam %s" % domejn)
    url = u'http://dns.marnet.net.mk/registar.php?dom=' + domejn
    
    if gae:
        result = urlfetch.fetch(url, deadline=60)
        strana = result.content
    else:
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        strana = res.read()
    
    soup = BeautifulSoup(strana)
    regstring = """ .mk """  # Greska vo sistemot na marnet
    if regstring in strana: 
        return               # TODO: vidi dali ja ima vo db i signaliziraj brisenje
    c = conn.cursor()    
    p1 = soup('table')[6].blockquote.text[-10:]
    
    if p1[6:].isdigit():
        p1 = p1[6:] + '-' + p1[3:6] + p1[0:2]
    else:
        p1 = '2014-12-31'
    p2 = soup('td')[36].text
    if p2[6:].isdigit():
        p2 = p2[6:] + '-' + p2[3:6] + p2[0:2]
    else:
        p2 = '2003-05-01'
    p3 = soup('td')[38].text
    p4 = soup('td')[40].text
    p5 = soup('td')[42].text
    p6 = soup('td')[44].text
    p7 = soup('td')[49].text
    p8 = soup('td')[51].text
    p9 = soup('td')[53].text
    p10 = soup('td')[56].text
    p11 = soup('td')[58].text
    p12 = soup('td')[60].text
    p13 = soup('td')[65].text
    p14 = soup('td')[67].text
    p15 = datetime.datetime.now()
    p16 = 1
    p17 = 'Y'
    promena = False;
    c.execute("""select * from domaininfo where domen=%s and status='Y'""",(domejn,))
    row = c.fetchone();
    if row is None: 
        logging.info(u"Nov Domen")
        promena = True;
        p16 = 1
    elif (row[0],row[1].isoformat(), row[2].isoformat(), row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14]) != (domejn,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14):
        logging.info("Razlichni se ")
        promena = True
        c.execute("""select version from domaininfo where domen=%s and status='Y'""",(domejn,))
        p16 = c.fetchone()[0]+1;
        c.execute("""update domaininfo set status='N' where domen=%s and status = 'Y'""",(domejn,))
    if promena == True: 
        c.execute('insert into domaininfo values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (domejn,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17))
        conn.commit()
    c.close()


def sochuvaj_domejni(domejni):
    """Ги сочувува домејните во база"""

    if not domejni:
        return False

    if gae:
        conn = rdbms.connect(instance=_INSTANCE_NAME, database='domaininfo')
    else:
        pass
        #conn = sqlite3.connect("db/domaininfo.sqlite3") #GAEquirk
        
    for domejn in domejni:
        i = 0
        while True:
            try:
                i = i + 1
                dodaj_domejn(domejn,conn)
                break
            except (urllib2.URLError, apiproxy_errors.DeadlineExceededError, urlfetch_errors.DeadlineExceededError, urlfetch_errors.DownloadError, urlfetch_errors.Error):
                logging.error('Internet greshka, probuvam pak: ' + domejn)
                if i == 3: break
        

if __name__=="__main__":
    logging.info('Pocnuvam')
    stranici = stranici()
    domejni = zemi_domejni(stranici)
    
    if domejni == []:
        fajl = open('domejni.pckl','rb')
        domejni = pickle.load(fajl)
        fajl.close()
    
    if domejni:
        logging.info('Snimam domeni')
        sochuvaj_domejni(domejni)
