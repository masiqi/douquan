#-*-coding:utf8;-*-
from django.db import models
from member.models import User
from deal.models import Deal

MYDEAL_TYPE_CHOICE = (
    (1, u'公开'),
    (2, u'不公开'),
)
MYDEAL_STATUS_CHOICE = (
    (1, u'未使用'),
    (2, u'已使用'),
)
MYDEAL_LIMIT_CHOICE = (
    (1, u'有期限'),
    (2, u'无期限'),
)

class Mydeal(models.Model):
    user = models.ForeignKey(User, db_index=True, related_name='user_mydeal')
    deal = models.ForeignKey(Deal, db_index=True, null=True, blank=True, related_name='deal_mydeal')
    name = models.CharField('name', max_length=255)
    url = models.URLField('url', max_length=255)
    site = models.CharField('site', max_length=32)
    price = models.FloatField('price')
    account = models.CharField('account', max_length=32, blank=True, null=True)
    type = models.SmallIntegerField(choices=MYDEAL_TYPE_CHOICE, db_index=True, default='1')
    status = models.SmallIntegerField(choices=MYDEAL_STATUS_CHOICE, db_index=True, default='1')
    created_at = models.DateTimeField('create date', db_index=True, auto_now_add=True)
    updated_at = models.DateTimeField('update date', auto_now=True)
    used_at = models.DateTimeField('used date', blank=True, null=True)
    deadline = models.DateTimeField('deadline', blank=True, null=True)
    reserve = models.DateTimeField('reserve', blank=True, null=True)
    limit = models.SmallIntegerField(choices=MYDEAL_LIMIT_CHOICE, db_index=True, default='1')
