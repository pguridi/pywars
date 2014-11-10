from django.contrib import admin
from django.conf.urls import patterns
from django.http import HttpResponse
import itertools

# Register your models here.

from game.models import (
    Bot,
    Challenge,
    UserProfile,
    FinalChallenge,
)

class UserProfileAdmin(admin.ModelAdmin):
    pass
admin.site.register(UserProfile, UserProfileAdmin)

class BotAdmin(admin.ModelAdmin):
    pass
admin.site.register(Bot, BotAdmin)

class ChallengeAdmin(admin.ModelAdmin):
    pass
admin.site.register(Challenge, ChallengeAdmin)


class FinalChallengeAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super(FinalChallengeAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^final_challenge/$', self.final_challenge)
        )
        return my_urls + urls

    def final_challenge(self, request):
        profiles = UserProfile.objects.filter(user__is_superuser=False).all()
        final_challenge = FinalChallenge()
        for x, y in itertools.product(profiles, repeat=2):
            if x == y:
                continue
            challenge = Challenge()
            challenge.requested_by = x
            challenge.challenger_bot = x.current_bot
            challenge.challenged_bot = y.current_bot
            challenge.save()
            final_challenge.add(challenge)
        final_challenge.save()
        return HttpResponse('/')

admin.site.register(FinalChallenge, FinalChallengeAdmin)
