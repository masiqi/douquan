from django.template import Node, Template, Context, Variable, TemplateSyntaxError
from django.template import Library
from django.conf import settings
from django.utils.encoding import smart_str
from tagging.models import Tag
from deal.models import Category, City, Company, Comment, Deal, Local, Site, Transfer

register = Library()

class cityLocalsNode(Node):
    def __init__(self, city_id, var):
        self.city_id = Variable(city_id)
        self.var_name = var
    def render(self, context):
        context[self.var_name] = Local.objects.get_local_by_city_id(self.city_id.resolve(context))
        return ''

@register.tag(name="city_locals")
def city_locals(parser, token):
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' takes at least two arguments"
                                  " (path to a view)" % bits[0])
    city_id = bits[1]
    var = bits[2]
    return cityLocalsNode(city_id, var)


class CategoriesNode(Node):
    def __init__(self, var):
        self.var_name = var
    
    def render(self, context):
        context[self.var_name] = Category.objects.all()
        return ''
    
@register.tag(name="categories")
def categories(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least two arguments"
                                  " (path to a view)" % bits[0])
    var = bits[1]
    return CategoriesNode(var)

    
class TagsNode(Node):
    def __init__(self, var):
        self.var_name = var
    
    def render(self, context):
        context[self.var_name] = Tag.objects.all()
        return ''
    
@register.tag(name="tags")
def tags(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least two arguments"
                                  " (path to a view)" % bits[0])
    var = bits[1]
    return TagsNode(var)

class DealCommentsNode(Node):
    def __init__(self, deal_id, var):
        self.deal_id = Variable(deal_id)
        self.var_name = var
    
    def render(self, context):
        context[self.var_name] = Comment.objects.get_comments_by_deal_id(self.deal_id.resolve(context))[:settings.DEFAULT_ENTRIES]
        return ''
    
@register.tag(name="deal_comments")
def deal_comments(parser, token):
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' takes at least two arguments"
                                  " (path to a view)" % bits[0])
    deal_id = bits[1]
    var = bits[2]
    return DealCommentsNode(deal_id, var)    

class DealTransfersNode(Node):
    def __init__(self, deal_id, var):
        self.deal_id = Variable(deal_id)
        self.var_name = var
    
    def render(self, context):
        context[self.var_name] = Transfer.objects.get_transfers_by_deal(self.deal_id.resolve(context))[:settings.DEFAULT_ENTRIES]
        return ''
    
@register.tag(name="deal_transfers")
def deal_transfers(parser, token):
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' takes at least two arguments"
                                  " (path to a view)" % bits[0])
    deal_id = bits[1]
    var = bits[2]
    return DealTransfersNode(deal_id, var)  

class CategoryDealsNode(Node):
    def __init__(self, city_id, category_id, deal_id, var):
        self.city_id = Variable(city_id)
        self.category_id = Variable(category_id)
        self.deal_id = Variable(deal_id)
        self.var_name = var
    
    def render(self, context):
        context[self.var_name] = Deal.objects.get_deals_by_category(self.city_id.resolve(context), self.category_id.resolve(context), self.deal_id.resolve(context))[:settings.DEFAULT_ENTRIES]
        return ''
    
@register.tag(name="category_deals")
def category_deals(parser, token):
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' takes at least two arguments"
                                  " (path to a view)" % bits[0])
    city_id = bits[1]
    category_id = bits[2]
    deal_id = bits[3]
    var = bits[4]
    return CategoryDealsNode(city_id, category_id, deal_id, var)
