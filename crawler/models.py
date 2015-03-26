import time
import datetime
from django.db import models
from django.contrib import admin
from deal.models import Site

ENTRY_TYPE_CHOICE = (
    (1, u'url'),
    (2, u'file'),
)

VAR_TYPE_CHOICE = (
    (1, u'list'),
    (2, u'text'),
    (3, u'static'),
)

VAR_CHANNEL_CHOICE = (
    (1, u'page'),
    (2, u'list'),
)

class TaskManager(models.Manager):
    def get_task_by_id(self, task_id):
        try:
            task = self.get(pk=task_id)
            return task
        except Task.DoesNotExist:
            return None
        
class Task(models.Model):
    name = models.CharField('name', max_length=255, db_index=True)
    site = models.ForeignKey(Site, related_name='site_task')
    charset = models.CharField('charset', max_length=16, default="utf8")
    
    objects = TaskManager()
    
    def __unicode__(self):
        return self.name
    
class Entry(models.Model):
    task = models.ForeignKey(Task, db_index=True, related_name='task_entry')
    source = models.CharField('source', max_length=255)
    type = models.SmallIntegerField(choices=ENTRY_TYPE_CHOICE, db_index=True, default='1')
    cookie = models.TextField('cookie', blank=True, null=True)
    
    def __unicode__(self):
        return self.task.name + '_' + self.source + '_' + str(self.cookie)
    
class PublishRuleManager(models.Manager):
    def get_publishrules_by_task_id(self, task_id):
        return self.filter(task__id=task_id)
    
class PublishRule(models.Model):
    task = models.ForeignKey(Task, db_index=True, related_name='task_publishrule')
    name = models.CharField('name', max_length=255)
    process = models.CharField('process', max_length=255, blank=True, null=True)
    auto_update = models.BooleanField('auto update', default=False)
    default_value = models.TextField('default value', blank=True, null=True)
    
    objects = PublishRuleManager()

    def __unicode__(self):
        return self.task.name + '_' + self.name
    
class UrlRule(models.Model):
    entry = models.ForeignKey(Entry, db_index=True, related_name='entry_urlrule')
    regular = models.CharField('regular', max_length=255)
    process = models.CharField('process', max_length=255, blank=True, null=True)
    
    def __unicode__(self):
        return self.entry.task.name + '_' + self.regular
    
class UniVarManager(models.Manager):
    def get_list_var_by_entry(self, entry):
        return self.filter(entry=entry, type=1)
    
    def get_text_var_by_entry(self, entry):
        return self.filter(entry=entry, type=2)

    def get_static_var_by_entry(self, entry):
        return self.filter(entry=entry, type=3)

    def get_all_var_by_entry(self, entry):
        return self.filter(entry=entry)

class UniVar(models.Model):
    entry = models.ForeignKey(Entry, db_index=True, related_name='entry_var')
    name = models.CharField('name', max_length=255, db_index=True)
    regular = models.CharField('regular', max_length=255)
    process = models.CharField('process', max_length=255, blank=True, null=True)
    type = models.SmallIntegerField(choices=VAR_TYPE_CHOICE, db_index=True, default='2')
    
    objects = UniVarManager()

    def __unicode__(self):
        return self.entry.task.name + '_' + self.name
    
class TaskVarManager(models.Manager):
    def get_all_var_by_task(self, task):
        return self.filter(task=task)
    
class TaskVar(models.Model):
    task = models.ForeignKey(Task, db_index=True, related_name='task_var')
    name = models.CharField('name', max_length=255, db_index=True)
    regular = models.CharField('regular', max_length=255)
    process = models.CharField('process', max_length=255, blank=True, null=True)
    type = models.SmallIntegerField(choices=VAR_TYPE_CHOICE, db_index=True, default='2')
    
    objects = TaskVarManager()

    def __unicode__(self):
        return self.task.name + '_' + self.name
    

class StorageManager(models.Manager):
    def get_storage_by_id(self, storage_id):
        try:
            storage = self.get(pk=storage_id)
            return storage
        except Storage.DoesNotExist:
            return None
    
    def get_storage_by_task_id(self, task_id, within=3600):
	now = time.time()
	update_at = datetime.datetime.fromtimestamp(now - within)
        return self.filter(task__id=task_id, updated_at__gte=update_at)
        
class Storage(models.Model):
    task = models.ForeignKey(Task, db_index=True, related_name='task_storage')
    url = models.CharField('url', max_length=255, db_index=True)
    content = models.TextField('content')
    updated_at = models.DateTimeField('update date', auto_now=True)
    
    objects = StorageManager()
    
    class Meta:
        unique_together = (("task", "url"),)
        
    def __unicode__(self):
        return self.task.name + '_' + self.url
    
class Resource(models.Model):
    url = models.CharField('url', max_length=255, db_index=True, primary_key=True)
    path = models.CharField('path', max_length=255)
    
admin.site.register(Task)
admin.site.register(Entry)
admin.site.register(UrlRule)
admin.site.register(PublishRule)
admin.site.register(UniVar)
admin.site.register(TaskVar)
admin.site.register(Storage)
