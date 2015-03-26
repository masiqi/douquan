#-*- coding: utf-8 -*-
from django import template
from django.utils.translation import ugettext
import urllib,re
import datetime
try:
    import json
except:
    import simplejson as json

register = template.Library()

#url编码
@register.filter
def quotegbk(value):
    return urllib.quote(value.encode('gbk'))
@register.filter
def quoteutf8(value):
    return urllib.quote(value.encode('utf8'))

@register.filter
def img_replace(value):
    return value.replace('src="/media/deal_pic/', 'src="http://img.douquan.com/media/deal_pic/')

@register.filter
def js(value):
    return json.dumps(value)

@register.filter
def splitToBB(value):
    p = re.compile( '(\d)')
    return p.sub(r'<b>\1</b>' , str(value))
@register.filter
def cutChinese(value, arg):
    try:
        value.decode('utf8')
        return value[:6]
    except:
        return value[:arg].encode('utf8') + '...'

@register.filter
def myyingkuiclass(yingkui, yingkuiclass):
    try:
        if abs(float('%.3f' % float(yingkui))) == 0:
            return ''
        else:
            return yingkuiclass
    except:
        return ''


@register.filter(name='mytime')
def mytime(d):
    if d.__class__ is not datetime.datetime:
        d = datetime.datetime(d.year, d.month, d.day)

    now = datetime.datetime.now()
    if not now:
        if d.tzinfo:
            now = datetime.datetime.now(LocalTimezone(d))
        else:
            now = datetime.datetime.now()

    # ignore microsecond part of 'd' since we removed it from 'now'
    delta = now - (d - datetime.timedelta(0, 0, d.microsecond))
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0:
        return u'0 ' + '分钟前'
    if since < 3600:
        return str(since/60) + '分钟前'
    elif since >= 3600 and since < 86400:
        return str(since/3600) + '小时前'
    else:
        return d.strftime("%y年%m月%d日")
