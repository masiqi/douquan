#-*-coding:utf8;-*-
import MySQLdb
import datetime
import time
import httplib
from urlparse import urlparse

from django.core.management.base import BaseCommand, CommandError
from deal.models import Deal, Site, City, Category

class Command(BaseCommand):
    help = '设置团购状态'

    def handle(self, *args, **options):
        self._set_deals()
        
    def _set_deals(self):
        """
        获取正在团购的物品
        @author: xiaoye
        @param start_date: 起始时间
        @type start_date: datetime
        """
        deals = Deal.objects.filter(status=1)
        for deal in deals:
            end_at = deal.end_at
            if self._check_status(end_at) is True:
                deal.status = 3
                deal.save()

    def _check_status(self, end_at):
        """
        检查团购信息是否已经过期
        @param end_at: 团购结束时间
        """
        now = datetime.datetime.now()
        if now > end_at:
            return True
        return False
