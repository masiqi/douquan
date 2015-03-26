from django.contrib import admin
from member.models import User, Score, ScoreChannel, ScoreLog, ScoreRule, Active, Forget

admin.site.register(User)
admin.site.register(Score)
admin.site.register(ScoreChannel)
admin.site.register(ScoreLog)
admin.site.register(ScoreRule)
admin.site.register(Active)
admin.site.register(Forget)
