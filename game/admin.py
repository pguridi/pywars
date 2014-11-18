from django.contrib import admin
from django.conf.urls import patterns
from django.http import HttpResponseRedirect
from game.tasks import validate_bot
import itertools

# Register your models here.

from game.models import (
    Bot,
    Challenge,
    UserProfile,
    FinalChallenge,
)
from game.tasks import run_match


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'current_bot', 'code_update_date')
    list_filter = ('current_bot',)


class BotAdmin(admin.ModelAdmin):
    actions = ['validate_bot']
    list_display = ('creation_date', 'modification_date', 'owner', 'valid')
    list_filter = ('valid',)
    
    def validate_bot(self, request, queryset):
        for bot in queryset:
            validate_bot.delay(bot.id, bot.code)

class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('creation_date', 'requested_by', 'challenger_bot', 'challenged_bot', 'played', 'winner_player', 'canceled')
    list_filter = ('canceled', 'final_challenge')
    

class FinalChallengeAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super(FinalChallengeAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^final_challenge/$', self.final_challenge)
        )
        return my_urls + urls

    actions = ['final_challenge']
    
    def final_challenge(self, request, queryset):
        profiles = UserProfile.objects.filter(user__is_superuser=False, user__is_active=True).all()
        if not queryset:
		return HttpResponseRedirect('/admin')
        final_challenge = queryset[0]
        for up_player1, up_player2 in itertools.product(profiles, repeat=2):
            if (up_player1 == up_player2
                or not up_player1.current_bot
                or not up_player2.current_bot):
                continue
            challenge = Challenge()
            challenge.requested_by = up_player1
            challenge.challenger_bot = up_player1.current_bot
            challenge.challenged_bot = up_player2.current_bot
            challenge.final_challenge = final_challenge
            challenge.save()
            final_challenge.challenge_set.add(challenge)
            # dispatch the new task
            players = {up_player1.user.username: up_player1.current_bot.code,
                       up_player2.user.username: up_player2.current_bot.code,
            }
            run_match.delay(challenge.id, players)

        final_challenge.save()
        return HttpResponseRedirect('/admin')

admin.site.register(FinalChallenge, FinalChallengeAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Bot, BotAdmin)
