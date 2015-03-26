#-*-coding:utf8;-*-
import MySQLdb
import datetime
import time
import httplib
from urlparse import urlparse
from BeautifulSoup import BeautifulSoup

from django.core.management.base import BaseCommand, CommandError
from deal.models import Deal, Site, City, Picture, Category

DB_HOST = "192.168.1.221"
DB_NAME = "douquancms"
DB_USER = "douquan"
DB_PASS = "douquan"

class Command(BaseCommand):
    help = '抓取团购信息中的已购买人数'

    def handle(self, *args, **options):
        self._get_deals()
        
    def _get_deals(self):
        """
        获取正在团购的物品
        @author: xiaoye
        @param start_date: 起始时间
        @type start_date: datetime
        """
        deals = Deal.objects.filter(status=1)
        for deal in deals:
            html = self._get_html(deal.url)
            volunteer = self._get_volunteer(deal.site.url, html)
            self._update(deal, volunteer)

    def _get_html( self, url ):
        """
        抓取指定url的html数据
        """
        url_parsed = urlparse(url)
        site = url_parsed.netloc
        page = url_parsed.path
        try:
            httpconn = httplib.HTTPConnection(site)
            httpconn.request("GET", page)
            resp = httpconn.getresponse()
            resppage = resp.read()
        except:
            resppage = ""

        return resppage
    
    def _get_volunteer(self, site_url, html):
        """
        分析html，获取已购买人数
        @param site_url 网站类别(采用不同的html分析方法)
        @param html html代码
        """
        soup = BeautifulSoup(html)
        if site_url == "http://www.meituan.com":
            v = soup.find('p', {"class":"deal-buy-tip-top"})
            volunteer = int(v.contents[0].string)
        return volunteer
    
    def _update(self, deal, volunteer):
        """
        把已购买人数写入数据库(django\dedecms)
        """
        deal.volunteer = volunteer
        deal.save()
        
        query = "update `dede_addonarticle17` set amount_buyer=%d where original_url='%s'" % (volunteer, deal.url)
        db=MySQLdb.connect(host=DB_HOST,user=DB_USER,passwd=DB_PASS,db=DB_NAME, charset="utf8")
        c=db.cursor()
        c.execute(query)
        c.close()
        db.close()
                
        return
