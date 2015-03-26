#-*-coding:utf8;-*-
import MySQLdb
import datetime
import time
from urlparse import urlparse
import re

from django.core.management.base import BaseCommand, CommandError
from deal.models import Deal, Site, City, Category

DB_HOST = "192.168.1.221"
DB_NAME = "douquancms_dev"
DB_USER = "douquan"
DB_PASS = "douquan"

CMS_NAME = "douquancms_dev"

class Command(BaseCommand):
    help = 'scrap groupon data from database which is belong to dedecms'

    def handle(self, *args, **options):
        start_date = datetime.datetime(int(args[0]), int(args[1]), int(args[2]))
        art_list = self._get_articles(start_date)
        self.sync2db(art_list)
        #self._format_title()
#        deals = Deal.objects.filter(site=3)
#        for deal in deals:
#            deal.company_detail = deal.company_detail[0:-6]
#            deal.save()
        
    def _format_title(self):
        deals = Deal.objects.all()
        for deal in deals:
            r = re.compile(ur'(仅售\d*元(!|！))')
            title = r.sub('', deal.title)
            r = re.compile(ur'(原价\d*元)')
            deal.title = r.sub('', title)
            deal.save()
        return
    
    def _get_articles(self, start_date=""):
        """
        获取dedecms抓取到的文章
        @author: xiaoye
        @param start_date: 起始时间
        @type start_date: datetime
        """
        
        start_timestamp = int(time.mktime(start_date.timetuple()))
        query = "SELECT dede_archives.id, dede_addonarticle17.shop_detail, dede_archives.title, \
dede_archives.litpic,  dede_addonarticle17.body, \
dede_addonarticle17.original_price, dede_addonarticle17.price, \
dede_addonarticle17.original_url, dede_addonarticle17.shop_name, \
dede_addonarticle17.city, dede_archives.id, dede_addonarticle17.amount_buyer, \
dede_addonarticle17.begin, dede_addonarticle17.end, dede_addonarticle17.deadline, dede_addonarticle17.category \
FROM dede_archives,dede_addonarticle17 \
where dede_archives.id=dede_addonarticle17.aid and dede_archives.channel=17 and dede_archives.pubdate > %d order by dede_archives.pubdate desc"
        query = query % start_timestamp
        db=MySQLdb.connect(host=DB_HOST,user=DB_USER,passwd=DB_PASS,db=DB_NAME, charset="utf8")
        c=db.cursor()
        c.execute(query)
        articles = c.fetchall()
        c.close()
        db.close()
        
        art_list = []
        
        for art in articles:
            tags = self._get_tags(art[10])
            deal = {
                    'title' : art[2],
                    'body' : art[4],
                    'price' : art[6],
                    'original_price' : art[5],
                    'shop_detail' : art[1],
                    'shop_name' : art[8],
                    'litpic' : art[3],
                    'url' : art[7],
                    'city' : art[9],
                    'volunteer' : art[11],
                    'begin' : art[12],
                    'end' : art[13],
                    'deadline' : art[14],
                    'category' : art[15],
                    'tags' : tags,
                    }
            art_list.append(deal)
            
        return art_list
    
    def _get_tags(self, aid):
        """
        取文章tags
        """
        query = "select * from dede_taglist where aid=%d and typeid=2" % aid
        db=MySQLdb.connect(host=DB_HOST,user=DB_USER,passwd=DB_PASS,db=DB_NAME, charset="utf8")
        c=db.cursor()
        c.execute(query)
        tags = c.fetchall()
        c.close()
        db.close()
        
        tags_text = ""
        for tag in tags:
            tags_text += tag[4] + " "
        
        return tags_text[:-1]
    
    def _get_site(self, sites, url):
        url_parsed = urlparse(url)
        for site in sites:
            site_url = site.url
            if site_url.find(url_parsed.netloc) != -1:
                return site
    
    def _get_city(self, cities, city_text):
        for city in cities:
            if city.name == city_text:
                return city
    
    def _format_datetime(self, date_string):
    	if date_string.find('|') == -1:
	        try:
	            rt = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
	        except:
	            rt = None
	else:
	        try:
	            rt = datetime.datetime.strptime(date_string, "%Y-%m-%d|%H:%M:%S")
	        except:
	            rt = None
        return rt
    
    def _get_category(self, category_string):
        if category_string != "":
            category, created = Category.objects.get_or_create(name=category_string)
        else:
            category = None
        return category
    
    def _get_status(self, begin, end):
        now = datetime.datetime.now()
        rest_of_time = end - now
        hours = rest_of_time.days * 36 + rest_of_time.seconds/3600
        if hours >= 0:
            return 1
        else:
            return 3
    
    def sync2db(self, art_list):
        """
        把文章列表写入物品数据库
        @param art_list: 文章列表
        @type art_list: List 
        """
        sites = Site.objects.all()
        cities = City.objects.all()
        for art in art_list:
            print art['title']
            if art['url'] != "":
                site = self._get_site(sites, art['url'])
                city = self._get_city(cities, art['city'])
                print site, city
                if city is None:
                    continue
                if site is None:
                    continue
                try:
                    deal = Deal.objects.get(site=site, name=art['title'], url=art['url'])
                except:
                    deal = Deal(
                            site = site,
                            name = art['title'],
                            detail = art['body'].replace(CMS_NAME+'/uploads/allimg', 'site_media/allimg'),
                            current_price = str(art['price']),
                            original_price = str(art['original_price']),
                            url = art['url'],
                            buy_url = art['url'],
                            company_name = art['shop_name'],
                            company_detail = art['shop_detail'],
                            volunteer = art['volunteer'],
                            begin_at = self._format_datetime(art['begin']),
                            end_at = self._format_datetime(art['end']),
                            accomplish_at = self._format_datetime(art['deadline']),
                            category = self._get_category(art['category']),
                            logo = art['litpic'].replace(CMS_NAME+'/uploads/allimg', 'site_media/allimg'),
                            )
                    deal.save()
                deal.city.add(city)
                deal.begin_at = self._format_datetime(art['begin'])
                deal.end_at = self._format_datetime(art['end'])
                deal.status = self._get_status(deal.begin_at, deal.end_at)
                if art['tags'] != "":
                    deal.tags = art['tags']
                deal.save()
