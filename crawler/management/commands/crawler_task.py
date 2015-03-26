#-*-coding:utf8;-*-
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from crawler.models import Storage
from crawler.func import CrawlerTask, CrawlerStorage, Publish, import_city, update_cookie

class Command(BaseCommand):
    help = "crawler"

    output_transaction = True

    def handle(self, *args, **options):
        func = args[0]
        if func == "update":
            task_id = args[1]
            ct = CrawlerTask(task_id, False) 
            ct.run()
        if func == "read_task":
            task_id = args[1]
            storages = Storage.objects.get_storage_by_task_id(task_id)
            for storage in storages:
                print storage.content
        if func == "read_storage":
            storage_id = args[1]
            cs = CrawlerStorage(storage_id)
            x = cs.storage2string()
            for k,v in x.iteritems():
                print "%s" % k 
                print v
        if func == "read_url":
            url = args[1]
	    storage = Storage.objects.get(url=url)
            cs = CrawlerStorage(storage.id)
            x = cs.storage2string()
            for k,v in x.iteritems():
                print "%s" % k 
                print v
        if func == "publish":
            task_id = args[1]
            p = Publish(task_id)
            p.publish()
        if func == "init_publishrule":
            task_id = args[1]
            p = Publish(task_id)
            p.init_publishrule()
	if func == "import_city":
	    import_city()
	if func == "update_cookie":
	    task = args[1]
	    update_cookie(task)
