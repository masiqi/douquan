import time
import datetime
from django.db import models
from django.contrib import admin

STATUS_CHOICE = (
    ('0', 'register'),
    ('1', 'active'),
    ('2', 'block'),
)

SCORE_TYPE_CHOICE = (
    (0, u'in'),
    (1, u'out'),
)

LIMIT_TYPE_CHOICE = (
    (0, u'unlimted'),
    (1, u'today'),
    (2, u'second'),
    (3, u'total'),
)

class UserManager(models.Manager):
    def get_user_by_id(self, user_id = None):
        try:
            return self.get(pk=user_id)
        except User.DoesNotExist:
            return None
    
class User(models.Model):
    email = models.EmailField("email", db_index=True, unique=True)
    name = models.CharField("name", max_length=16)
    password = models.CharField("password", max_length=16)
    status = models.SmallIntegerField(choices=STATUS_CHOICE, default=0, db_index=True)
    created_at = models.DateTimeField('create date', auto_now_add=True)
    
    objects = UserManager()
    
    def __unicode__(self):
        return self.name

class Active(models.Model):
    user = models.OneToOneField(User, related_name="active", primary_key=True)
    password = models.CharField("password", max_length=16)
    
class Forget(models.Model):
    user = models.OneToOneField(User, related_name="forget", primary_key=True)
    password = models.CharField("password", max_length=16)
    
class Score(models.Model):
    user = models.OneToOneField(User, related_name="score", primary_key=True)
    score = models.IntegerField("score", default=0, db_index=True)
    experience = models.IntegerField("experience", default=0, db_index=True)
    
    def __unicode__(self):
        return self.user.name

class ScoreLogManager(models.Manager):
    def change_score(self, user_id, score, type, channel, limit=None):
        if int(type) == 0 and limit is not None:
            if limit['type'] == 0:
                count = self.filter(user__id=user_id, type=type, channel=channel, created_at__gte=datetime.date.today() ).aggregate(models.Sum('score'))
                if count['score__sum'] >= limit['count']:
                    return False
            if limit['type'] == 1:
                now = time.time()
                count = self.filter(user__id=user_id, type=type, channel=channel, created_at__gte=datetime.date.fromtimestamp(now - limit['second'])).aggregate(models.Sum('score'))
                if count['score__sum'] >= limit['count']:
                    return False
        if int(type) == 1:
            total = self.filter(user__id=user_id, type=0).aggregate(models.Sum('score'))
            used = self.filter(user__id=user_id, type=1).aggregate(models.Sum('score'))
            if total['score__sum'] - used['score__sum'] < score:
                return False
        log = ScoreLog(user__id = user_id, score = score, type = type, channel = channel)
        log.save()
        total = self.filter(user__id=user_id, type=0).aggregate(models.Sum('score'))
        used = self.filter(user__id=user_id, type=1).aggregate(models.Sum('score'))
        s, created = Score.objects.get_or_create(user__id=user_id, defaults={'user_id':user_id, 'experience':total, 'score':total-used})
        if created == False:
            s.experience = total
            s.score = total - used
        s.save()
        return True
    
class ScoreChannel(models.Model):
    name = models.CharField('name', max_length=16, unique=True)
    
    def __unicode__(self):
        return self.user.name
    
class ScoreLog(models.Model):
    user = models.ForeignKey(User, db_index=True, related_name='user_scorelog')
    score = models.IntegerField("score", default=0)
    type = models.SmallIntegerField(choices=SCORE_TYPE_CHOICE, default=0, db_index=True)
    channel = models.ForeignKey(ScoreChannel, db_index=True, related_name='channel_log')
    created_at = models.DateTimeField('create date', db_index=True, auto_now_add=True)
    
    objects = ScoreLogManager()
    
    def __unicode__(self):
        return self.user.name
    
class ScoreRule(models.Model):
    name = models.CharField('name', max_length=16, unique=True)
    score = models.IntegerField('score')
    limit_type = models.SmallIntegerField(choices=LIMIT_TYPE_CHOICE, default=0)
    limit = models.IntegerField('limit', default=0)
    second = models.IntegerField('second', null=True, blank=True) 
    channel = models.ForeignKey(ScoreChannel, db_index=True, related_name='channel_rule')
    
    def __unicode__(self):
        return self.user.name
    

#admin.site.register(User)
#admin.site.register(Score)
#admin.site.register(Active)
#admin.site.register(Forget)
