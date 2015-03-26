import urllib2
import re
import uuid
import datetime
import time
import base64
import cPickle as pickle
import pycurl
import StringIO
import cgi
from os.path import dirname, isdir
from os import makedirs, remove
from django.conf import settings
from django.core.urlresolvers import reverse
from libs.common import fix_url
from crawler.models import Entry, Task, Storage, Resource, PublishRule, UrlRule, UniVar  
from deal.models import Deal, Site, City

class CrawlerTask(object):
    def __init__(self, task_id, force_update=False):
        self.task_id = task_id
        self.task = Task.objects.get_task_by_id(self.task_id)
        self.force_update = force_update
        if self.task is None:
            raise Task.DoesNotExist
        self.task_entries = self.task.task_entry.all()
        
    def run(self):
        for entry in self.task_entries:
            if entry.type == 1:
                urls = self.process_url(entry)
            if entry.type == 2:
                urls = self.process_file(entry)
	    self.process_entry(entry, urls)
            
    def process_url(self, entry):
        #content = urllib2.urlopen(entry.source).read()
        content = self.fetch_content(entry.source, entry.cookie)
        url_list = []
        for rule in entry.entry_urlrule.all():
            temp_list = self.process_list(content, rule)
            self.unique_list(url_list, temp_list)
	return url_list

    def process_file(self, entry):
	f = file(entry.source)
	url_list = f.readlines()
	f.close()
	return url_list
    
    def process_entry(self, entry, url_list):
        entry_rules = entry.entry_var.get_all_var_by_entry(entry)
        task_rules = self.task.task_var.get_all_var_by_task(self.task)
        for url in url_list:
	    if entry.type == 1:
	        url = self.complate_url(url, entry.source, False)
	    deal = Deal.objects.get_deal_by_url(url)
	    if deal is None or deal.status == 1:
                t = self.fetch_content(url, entry.cookie)
	        try:
                    text = t.decode(self.task.charset)
                except:
                    text = t
	        real_url = self.get_real_url(text, task_rules, entry_rules, url)
                #text = urllib2.urlopen(url).read().decode(self.task.charset)
	        print real_url
	        deal = Deal.objects.get_deal_by_url(real_url)
	        if deal is None or deal.status == 1:
                    storage, created = Storage.objects.get_or_create(task=self.task, url=real_url, defaults={'task':self.task, 'url':real_url, 'content':pickle.dumps(self.process_rule(text, task_rules, entry_rules, real_url))})
                    if not created:
                        storage.content = pickle.dumps(self.process_rule(text, task_rules, entry_rules, real_url))
                        storage.save()
    
    def process_list(self, content, rule):
        re_name = re.compile('\(\?P<(\w+)>')
        has_name = True
        names = re_name.findall(rule.regular)
        if len(names) == 0:
            has_name = False
        if has_name:
	    l = []
            r = re.compile(rule.regular)
            for match in r.finditer(content):
                match_dict = match.groupdict()
                l.append(match_dict[names[0]])
	    return l
	else:
            r = re.compile(rule.regular)
            return r.findall(content)
    
    def process_list_rule(self, text, rule, url):
        return ''
    
    def process_text_rule(self, text, rule, url):
        rt = ''
        re_name = re.compile('\(\?P<(\w+)>')
        has_name = True
        names = re_name.findall(rule.regular)
        if len(names) == 0:
            has_name = False
        if has_name:
            r = re.compile(rule.regular)
            for match in r.finditer(text):
                match_dict = match.groupdict()
                rt = match_dict[names[0]]
		if rt is None and len(names) > 1:
                    rt = match_dict[names[1]]
		if rt is None and len(names) > 2:
                    rt = match_dict[names[2]]
                #return {rule.name:match_dict[names[0]]}
        else: 
            r = re.compile(rule.regular)
	    try:
                rt = r.findall(text)[0]
	    except:
		rt = ''
            #return {rule.name:r.findall(text)[0]}
        if len(rule.process) != 0:
	     #print rule.process + '('+ rt + ', ' + url+')'
            rt = eval('self.'+rule.process + '(rt, url)')
        return rt
    
    def process_static_rule(self, text, rule, url):
        rt  = rule.regular.split('=')[1]
	print rule.regular
	try:
            if len(rule.process) != 0:
                rt = eval('self.'+rule.process + '(rt, url)')
	except:
	    pass
        return rt
        
    def process_rule(self, text, task_rules, entry_rules, url):
        rt = {}
        for rule in task_rules:
            if int(rule.type) == 1:
                rt[rule.name] = self.process_list_rule(text, rule, url)
            if int(rule.type) == 2:
                rt[rule.name] = self.process_text_rule(text, rule, url)
            if int(rule.type) == 3:
                rt[rule.name] = self.process_static_rule(text, rule, url)
        for rule in entry_rules:
            if int(rule.type) == 1:
                rt[rule.name] = self.process_list_rule(text, rule, url)
            if int(rule.type) == 2:
                rt[rule.name] = self.process_text_rule(text, rule, url)
            if int(rule.type) == 3:
                rt[rule.name] = self.process_static_rule(text, rule, url)
        return rt
    
    def get_real_url(self, text, task_rules, entry_rules, url):
        rt = url
        for rule in task_rules:
            if int(rule.type) == 1 and rule.name == 'url':
                rt = self.process_list_rule(text, rule, url)
            if int(rule.type) == 2 and rule.name == 'url':
                rt = self.process_text_rule(text, rule, url)
            if int(rule.type) == 3 and rule.name == 'url':
                rt = self.process_static_rule(text, rule, url)
        for rule in entry_rules:
            if int(rule.type) == 1 and rule.name == 'url':
                rt = self.process_list_rule(text, rule, url)
            if int(rule.type) == 2 and rule.name == 'url':
                rt = self.process_text_rule(text, rule, url)
            if int(rule.type) == 3 and rule.name == 'url':
                rt = self.process_static_rule(text, rule, url)
        return rt
    
    def calculate_lefttime(self, text, source_url):
        now = time.time()
        try:
            x = int(now + int(text))
        except:
            x = int(now)
        return x
    
    def unescape(self, text, source_url):
        return cgi.unescape(text)
    
    def datetime2timestamp(self, text, source_url):
	x = text.rstrip().lstrip()
	if len(x) == 16:
	    dt = x + ':00'
	else:
	    dt = x 
	try:
	    st = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
	except:
	    st = time.mktime(datetime.date.today().timetuple()) + 86400
	return int(st)

    def calculate_lefttime1000(self, text, source_url):
        now = time.time()
        try:
            x = int(now + int(text)/1000)
        except:
            x = int(now)
        return x
    
    def calculate_lefttime10(self, text, source_url):
        now = time.time()
        try:
            x = int(now + int(text)/10)
        except:
            x = int(now)
        return x

    def end_at1000(self, text, source_url):
	try:
	    x = int(text)/1000
	except:
	    x = int(time.time())
	return x
    
    def calculate_lefttime_format(self, text, source_url):
        now = time.time()
	delta = 0
	r = re.compile('([\d]{1,2})')
	rt = r.findall(text)
	if len(rt) == 3:
	    delta += int(rt[0]) * 3600 + int(rt[1]) * 60 + int(rt[2])
	if len(rt) == 2:
	    delta += int(rt[0]) * 60 + int(rt[1])
	if len(rt) == 1:
	    delta += int(rt[0])
	return int(now + delta)

    def replace_span(self, text, source_url):
	rt = text.replace('<span>', '')
	rt = rt.replace('<SPAN>', '')
	rt = rt.replace('</SPAN>', '')
	rt = rt.replace('</span>', '')
	return rt

    def replace_comma(self, text, source_url):
	rt = text.replace(',', '')
	return rt

    def complate_img(self, text, source_url, auto_external=True):
	target = '<img src="' + text + '" />'
	return self.download_picture_and_delete_tags(target, source_url)

    def complate_url_buy(self, cUrl, source_url, auto_external=True):
	target = '/buy.php'+cUrl
	return self.complate_url(target, source_url, auto_external)

    def complate_url(self, cUrl, source_url, auto_external=True):
        r = re.search('(http|https)://([^/]*)', source_url)
        prefix = r.groups()[0] + '://' + r.groups()[1]
        path = source_url[:]
        
        if re.search(r'''^(http|https|ftp):(\/\/|\\\\)(([\w\/\\\+\-~`@:%])+\.)+([\w\/\\\.\=\?\+\-~`@':!%#]|(&amp;)|&)+''',cUrl,re.I) != None :
            target = cUrl
	elif cUrl == '':
	    return ''
        elif cUrl[:1] == '/' :
            target = prefix + cUrl
        elif cUrl[:3]=='../' :
            while cUrl[:3]=='../' :
                cUrl = cUrl[3:]
                if len(path) > 0 :
                    path = dirname(path)
                    target = path + '/' + cUrl
        elif cUrl[:2]=='./' :
            target = dirname(path) + cUrl[1:]
        else:
	    target = prefix + '/' + cUrl
	if auto_external:
	    try:
	        x = settings.SITE_INDEX + reverse("external_url", 'douquan.www.urls', args=(base64.b64encode(target),))
	    except:
	        x = settings.SITE_INDEX + reverse("external_url", 'douquan.www.urls', args=(base64.b64encode(target.encode('utf8')),))
	    return x
	else:
	    return target
        
    def download_picture_and_delete_tags(self, text, source_url):
        r = re.search('(http|https)://([^/]*)', source_url)
        prefix = r.groups()[0] + '://' + r.groups()[1]
        
        urls = re.findall(r'''(src|href|action)=(.+?)( |\/>|>|\r)''', text, re.I)
        if urls == None :
            return text
        else :
            media_dict = {}
            for url in urls:
                path = source_url[:]
                urlQuote = url[1]
                type = url[0]
                if len(urlQuote) > 0 and len(urlQuote) < 200 :
                    cUrl = re.sub('''['"]''','',urlQuote)
                else :
                    continue
                if re.search(r'''^(http|https|ftp):(\/\/|\\\\)(([\w\/\\\+\-~`@:%])+\.)+([\w\/\\\.\=\?\+\-~`@':!%#]|(&amp;)|&)+''',cUrl,re.I) != None :
                    target = cUrl
	        elif cUrl == '':
		    continue
                elif cUrl[:1] == '/' :
                    target = prefix + cUrl
                elif cUrl[:3]=='../' :
                    while cUrl[:3]=='../' :
                        cUrl = cUrl[3:]
                        if len(path) > 0 :
                            path = dirname(path)
                    target = path + '/' + cUrl
                elif cUrl[:2]=='./' :
                    target = dirname(path) + cUrl[1:]
                else:
		    target = prefix + '/' + cUrl
                if type == 'src':
                    if self.force_update == False:
                        try:
                            resource = Resource.objects.get(pk=target)
                            media_dict[target] = settings.MEDIA_FAKE_DIRECTORY + resource.path
                        except Resource.DoesNotExist:
                            resource = Resource(target, self.download_picture(target))
                            resource.save()
                            media_dict[target] = settings.MEDIA_FAKE_DIRECTORY + resource.path
                    else:
                        try:
                            resource = Resource.objects.get(pk=target)
                            remove(settings.MEDIA_ROOT + resource.path)
                            resource.path = self.download_picture(target)
                            resource.save()
                            media_dict[target] = settings.MEDIA_FAKE_DIRECTORY + resource.path
                        except Resource.DoesNotExist:
                            resource = Resource(target, self.download_picture(target))
                            resource.save()
                            media_dict[target] = settings.MEDIA_FAKE_DIRECTORY + resource.path
                    text = text.replace(cUrl, str(media_dict[target]))
                elif type == 'href':
		    try:
                        text = text.replace(cUrl, settings.SITE_INDEX + reverse("external_url", 'douquan.www.urls', args=(base64.b64encode(target),)), 1)
		    except:
                        text = text.replace(cUrl, settings.SITE_INDEX + reverse("external_url", 'douquan.www.urls', args=(base64.b64encode(target.encode('utf8')),)), 1)
            return text

    def download_picture(self, target):
	print target
	try:
            postfix = re.search('\.(\w+)(\?|$)', target).groups()[0]
	except:
	    postfix = 'png'
        r = re.search('(http://|https://)([\W\w].*?)(\?([\W\w].*)|$)', target.encode('utf8')).groups()
        if r[3] is None:
            req = r[0] + urllib2.quote(r[1])
        else:
            req = r[0] + urllib2.quote(r[1]) + '?' + r[3]
	try:
            data = urllib2.urlopen(req).read()
	except:
	    return ''
        uid = str(uuid.uuid1())
        date = datetime.date.today()
        directory = '/%04d%02d%02d' % (date.year, date.month, date.day)
        if not isdir(settings.MEDIA_ROOT + settings.MEDIA_SAVE_DIRECTORY + directory):
            makedirs(settings.MEDIA_ROOT + settings.MEDIA_SAVE_DIRECTORY + directory)
        file = open(settings.MEDIA_ROOT + settings.MEDIA_SAVE_DIRECTORY + directory + '/' + uid + '.' + postfix, 'w+b')
        file.write(data)
        file.close()
        return settings.MEDIA_SAVE_DIRECTORY + directory + '/' + uid + '.' + postfix

    def get_city_by_name(self, text, source_url):
	try:
	    city = City.objects.get(name=text)
	    return city.id
	except:
	    return '1'

    def unique_list(self, src_list, new_list):
        for l in new_list:
            if l not in src_list:
                src_list.append(l)
        return src_list

    def get_three(self, text, source_url):
	if text is not None and len(text) > 0:
	    return '3'
	else:
	    return '1'
    
    def fetch_content(self, url, cookies=''):
        crl = pycurl.Curl()
        crl.setopt(pycurl.VERBOSE,0)
        crl.setopt(pycurl.FOLLOWLOCATION, 1)
        crl.setopt(pycurl.MAXREDIRS, 5)
        crl.fp = StringIO.StringIO()
        crl.setopt(pycurl.URL, str(url))
        crl.setopt(crl.WRITEFUNCTION, crl.fp.write)
	if cookies != '':
            crl.setopt(pycurl.COOKIE, str(cookies))
        #crl.setopt(pycurl.HTTPHEADER, ["User-Agent: %s" % "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; CMS Music Store2 v1.00.09 (Music Store,1033); (R1 1.5); .NET CLR 1.1.4322)"])
        #crl.setopt(pycurl.HTTPHEADER, ["User-Agent: %s" % "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)"])
	if url.find("manzuo") == -1:
            crl.setopt(pycurl.HTTPHEADER, ["User-Agent: %s" % "Baiduspider+(+http://www.baidu.com/search/spider.htm)"])
        crl.perform()
	#rt = crl.fp.getvalue()
        return crl.fp.getvalue()
    
class CrawlerStorage(object):
    def __init__(self, storage_id):
        self.storage_id = storage_id
        self.storage = Storage.objects.get_storage_by_id(self.storage_id)
        if self.storage is None:
            raise Storage.DoesNotExist
        
    def storage2string(self):
        x = pickle.loads(str(self.storage.content))
        return x
        
class Publish(object):
    def __init__(self, task_id, force_update=False):
        self.task_id = task_id
        self.task = Task.objects.get_task_by_id(self.task_id)
        self.storages = Storage.objects.get_storage_by_task_id(task_id)
        self.publishrules = {}
        for r in PublishRule.objects.get_publishrules_by_task_id(task_id):
            self.publishrules[r.name] = r
        self.force_update = force_update
        if self.task is None:
            raise Task.DoesNotExist
        self.task_entries = self.task.task_entry.all()
        
    def init_publishrule(self):
	rule, created = PublishRule.objects.get_or_create(task=self.task, name='name', defaults={'task':self.task, 'name':'name', 'auto_update':True})
	rule, created = PublishRule.objects.get_or_create(task=self.task, name='detail', defaults={'task':self.task, 'name':'detail', 'auto_update':True})
	rule, created = PublishRule.objects.get_or_create(task=self.task, name='category_id', defaults={'task':self.task, 'name':'category_id', 'auto_update':False, 'default_value':''})
	rule, created = PublishRule.objects.get_or_create(task=self.task, name='site_id', defaults={'task':self.task, 'name':'site_id', 'auto_update':True, 'default_value':self.task.site.id})
	rule, created = PublishRule.objects.get_or_create(task=self.task, name='current_price', defaults={'task':self.task, 'name':'current_price', 'auto_update':True, 'default_value':1})
	rule, created = PublishRule.objects.get_or_create(task=self.task, name='original_price', defaults={'task':self.task, 'name':'original_price', 'auto_update':True, 'default_value':1})
	rule, created = PublishRule.objects.get_or_create(task=self.task, name='company_name', defaults={'task':self.task, 'name':'company_name', 'auto_update':True})
	rule, created = PublishRule.objects.get_or_create(task=self.task, name='company_detail', defaults={'task':self.task, 'name':'company_detail', 'auto_update':True})
	rule, created = PublishRule.objects.get_or_create(task=self.task, name='volunteer', defaults={'task':self.task, 'name':'volunteer', 'auto_update':True, 'default_value':50})
	rule, created = PublishRule.objects.get_or_create(task=self.task, name='min_actor', defaults={'task':self.task, 'name':'min_actor', 'auto_update':True, 'default_value':20})
	rule, created = PublishRule.objects.get_or_create(task=self.task, name='city_id', defaults={'task':self.task, 'name':'city_id', 'auto_update':True, 'default_value':1})
	rule, created = PublishRule.objects.get_or_create(task=self.task, name='buy_url', defaults={'task':self.task, 'name':'buy_url', 'auto_update':True, 'default_value':'http://www.bankrate.com.cn'})
	rule, created = PublishRule.objects.get_or_create(task=self.task, name='logo', defaults={'task':self.task, 'name':'logo', 'auto_update':True})
	rule, created = PublishRule.objects.get_or_create(task=self.task, name='end_at', defaults={'task':self.task, 'name':'end_at', 'auto_update':False})
	rule, created = PublishRule.objects.get_or_create(task=self.task, name='status', defaults={'task':self.task, 'name':'status', 'auto_update':True, 'default_value':'1'})

    def publish(self):
        for storage in self.storages:
            deal = Deal.objects.get_deal_by_url(storage.url)
            s = pickle.loads(str(storage.content))
            if deal is None:
                deal = Deal()
                deal.url = storage.url
                deal.name = s.get('name', self.publishrules.get('name').default_value)
                deal.detail = s.get('detail', self.publishrules.get('detail').default_value)
                deal.site_id = s.get('site_id', self.publishrules.get('site_id').default_value)
                deal.current_price = s.get('current_price', self.publishrules.get('current_price').default_value)
		if len(deal.current_price) > 5:
		    deal.current_price = self.publishrules.get('current_price').default_value
                if deal.current_price == '':
		    deal.current_price = self.publishrules.get('current_price').default_value
                deal.original_price = s.get('original_price', self.publishrules.get('original_price').default_value)
                if deal.original_price == '':
		    deal.original_price = self.publishrules.get('original_price').default_value
                deal.category_id= s.get('category_id', self.publishrules.get('category_id').default_value)
                deal.company_name = s.get('company_name', self.publishrules.get('company_name').default_value)
                deal.company_detail= s.get('company_detail', self.publishrules.get('company_detail').default_value)
                deal.volunteer = s.get('volunteer', self.publishrules.get('volunteer').default_value)
                if deal.volunteer == '':
		    deal.volunteer = self.publishrules.get('volunteer').default_value
                deal.min_actor = s.get('min_actor', self.publishrules.get('min_actor').default_value)
                deal.buy_url = s.get('buy_url', self.publishrules.get('buy_url').default_value)
                if deal.min_actor == '':
                    deal.min_actor = self.publishrules.get('min_actor').default_value
                try:
                    deal.end_at = datetime.datetime.fromtimestamp(s.get('end_at')) 
                except:
                    deal.end_at = datetime.date.today() + datetime.timedelta(days=1)
                try:
                    path = re.findall('src="(.*?)"', s.get('logo'))[0]
                except:
                    path = self.publishrules.get('logo').default_value
                deal.logo = path
		try:
                    deal.status = s.get('status', self.publishrules.get('status').default_value)
		except:
		    pass
                #deal.save()
		try:
                    deal.save()
                    city = City.objects.get(pk=s.get('city_id', self.publishrules.get('city_id').default_value))
                    deal.city.add(city)
		except:
		    print "faild : %s " % deal.url
		    pass
            else:
                if self.publishrules.get('name').auto_update:
                    deal.name = s.get('name', self.publishrules.get('name').default_value)
                if self.publishrules.get('detail').auto_update:
                    deal.detail = s.get('detail', self.publishrules.get('detail').default_value)
                if self.publishrules.get('site_id').auto_update:
                    deal.site_id = s.get('site_id', self.publishrules.get('site_id').default_value)
                if self.publishrules.get('current_price').auto_update:
                    deal.current_price = s.get('current_price', self.publishrules.get('current_price').default_value)
		    if len(deal.current_price) > 8 or deal.current_price == '':
			deal.current_price = self.publishrules.get('current_price').default_value
                if self.publishrules.get('original_price').auto_update:
                    deal.original_price = s.get('original_price', self.publishrules.get('original_price').default_value)
                    if deal.original_price == '':
		        deal.original_price = self.publishrules.get('original_price').default_value
                if self.publishrules.get('category_id').auto_update:
                    deal.category_id= s.get('category_id', self.publishrules.get('category_id').default_value)
                deal.company_name = s.get('company_name', self.publishrules.get('company_name').default_value)
                deal.company_detail= s.get('company_detail', self.publishrules.get('company_detail').default_value)
                deal.volunteer = s.get('volunteer', self.publishrules.get('volunteer').default_value)
                deal.min_actor = s.get('min_actor', self.publishrules.get('min_actor').default_value)
                deal.buy_url = s.get('buy_url', self.publishrules.get('buy_url').default_value)
                if deal.min_actor == '':
                    deal.min_actor = self.publishrules.get('min_actor').default_value
                if deal.volunteer == '':
                    deal.volunteer = self.publishrules.get('volunteer').default_value
                try:
                    deal.end_at = datetime.datetime.fromtimestamp(s.get('end_at')) 
                except:
                    deal.end_at = datetime.date.today() + datetime.timedelta(days=1)
                try:
                    path = re.findall('src="(.*?)"', s.get('logo').replace('\'', '"'))[0]
                except:
                    path = self.publishrules.get('logo').default_value
                deal.logo = path
                if self.publishrules.get('category_id').auto_update:
		    pass
                    #deal.category_id= s.get('category_id', self.publishrules.get('category_id').default_value)
		try:
                    if self.publishrules.get('status').auto_update:
                        deal.status= s.get('status', self.publishrules.get('status').default_value)
		except:
		    print "status faild : %s" % deal.url
		    pass
                #deal.save()
		try:
                    deal.save()
                    city = City.objects.get(pk=s.get('city_id', self.publishrules.get('city_id').default_value))
		    deal.city.clear()
                    deal.city.add(city)
		except:
		    print "faild : %s " % deal.url
		    pass

def import_city():
    from xpinyin.xpinyin import Pinyin
    from deal.models import City
    text = urllib2.urlopen('http://open.client.lashou.com/list/cities/').read().decode('utf8')
    r = re.compile('<cityname>([\W\w].*?)</cityname>')
    citys = r.findall(text)
    p = Pinyin('/home/website/douquan/libs/xpinyin/Mandarin.dat')
    for c in citys:
	cs = ''
	for char in c:
	    cs += p.get_initials(char)
	print c, cs
	try:
	    city = City.objects.get(name=c)
	    print "find"
	except:
	    city = City(name=c, abbreviation=cs.lower())
	    city.save()

def init_lashou():
    citys = {}
    task_id = 3
    cookie = 'city=%s;ThinkID=jenccjudbi910l63p20i3fg053'
    urlregular = '<div class="tit"><a href="(?P<url>[\W\w].*?)">'
    entries = ['http://www.lashou.com/deals.php', 'http://www.lashou.com/deals.php?page=2', 'http://www.lashou.com/deals.php?page=3', 'http://www.lashou.com/deals.php?page=4']
    text = urllib2.urlopen('http://open.client.lashou.com/list/cities/').read().decode('utf8')
    r = re.compile('<cityid>(?P<cid>[\d]*)</cityid><cityname>(?P<cname>[\W\w]*?)</cityname>')
    for i in r.findall(text):
	citys[i[1]] = i[0]
	c_cookie = cookie % i[0]
	print c_cookie
	try:
	    city = City.objects.get(name=i[1])
	except:
	    continue
	for e in entries:
	    entry, created = Entry.objects.get_or_create(task__id=task_id, cookie=c_cookie, source = e, defaults={'task_id':task_id, 'cookie':c_cookie, 'source':e})
	    urlrule, created = UrlRule.objects.get_or_create(entry=entry, regular=urlregular, defaults={'entry':entry, 'regular':urlregular, 'process':'complate_url'})
	    univar, created = UniVar.objects.get_or_create(entry=entry, name='city_id', defaults={'entry':entry, 'name':'city_id', 'type':3, 'regular':'city='+str(city.id)})

def update_cookie(task):
    if task == "manzuo":
        f = file('/tmp/manzuo.cookie')
	cookies = f.readlines()
        f.close()
	e = Entry.objects.get(pk=42)
	e.cookie = cookies[0]
	if len(e.cookie) > 2:
	    e.save()
	e = Entry.objects.get(pk=47)
	e.cookie = cookies[1]
	if len(e.cookie) > 2:
	    e.save()
	e = Entry.objects.get(pk=48)
	e.cookie = cookies[2]
	if len(e.cookie) > 2:
	    e.save()
