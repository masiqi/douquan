from django.http import HttpResponse
from deal.models import Deal, Vote
from deal.func import get_user_tagging, get_deal_tagging
import json

def _deal_review_info(request, deal_id):
    result = {}
    
    try:
        deal = Deal.objects.get(pk=deal_id)
    except:
        result = {}
        return HttpResponse(json.dumps(result), mimetype='text/html')
    
    if request.myuser is None:
        result['is_login'] = False
    else:
        result['is_login'] = True
        try:
            vote = Vote.objects.get(user__id = request.myuser.id, deal = deal)
            result['voted'] = True
        except:
            result['voted'] = False
    
    my_tags_list = []
    if result['is_login'] == True:
        my_tags = get_user_tagging(request.myuser.id)
        for mt in my_tags:
            my_tags_list.append(mt.tag.name)
        result['my_tags'] = ','.join(my_tags_list)
    
    deal_tags_list = []
    deal_tags = get_deal_tagging(deal.id)
    for dt in deal_tags:
        deal_tags_list.append(dt.tag.name)
    result['deal_tags'] = ','.join(deal_tags_list)
    
    vote_up_count = Vote.objects.filter(deal=deal, score='1').count()
    vote_dw_count = Vote.objects.filter(deal=deal, score='-1').count()
    result['up_count'] = vote_up_count
    result['dw_count'] = vote_dw_count
    return HttpResponse(json.dumps(result), mimetype='text/html')