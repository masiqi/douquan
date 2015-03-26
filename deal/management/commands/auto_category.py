#-*-coding:utf8;-*-
import re
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from deal.models import Category, Deal, AutoCategory

class Command(BaseCommand):
    help = "auto category"

    output_transaction = True

    def handle(self, *args, **options):
        func = args[0]
        if func == "update":
            type = args[1]
	    deals = []
	    if type == "all":
		deals = Deal.objects.all()
	    if type == "null":
		deals = Deal.objects.filter(category=None)
	    update_category(deals)
	if func == "init":
	    f = file(args[1])
	    k_list = f.readlines()
	    f.close()
	    for key in k_list:
		keyword, category_name, power = key.replace('\n', '').split(',')
		category, created = Category.objects.get_or_create(name=category_name, defaults={'name':category_name})
		ac = AutoCategory(keyword=keyword, category=category, power=power)
		try:
		   ac.save()
		except:
		   pass

def update_category(deals):
    acs = AutoCategory.objects.all().order_by('power')
    for deal in deals:
	for ac in acs:
	    if re.search(ac.keyword, deal.name) is not None:
	    #if deal.name.find(ac.keyword) != -1:
		deal.category = ac.category
	if deal.category is None:
	    #print deal.name
	    pass
	else:
	    deal.save()

