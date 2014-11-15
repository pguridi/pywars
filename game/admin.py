from django.contrib import admin
from django.conf.urls import patterns
from django.http import HttpResponseRedirect
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


admin.site.register(UserProfile, UserProfileAdmin)


class BotAdmin(admin.ModelAdmin):
    list_display = ('creation_date', 'modification_date', 'owner', 'valid')


admin.site.register(Bot, BotAdmin)


class ChallengeAdmin(admin.ModelAdmin):
    list_display = (
        'creation_date', 'requested_by', 'challenger_bot', 'challenged_bot', 'played', 'winner_player', 'canceled')


admin.site.register(Challenge, ChallengeAdmin)


class FinalChallengeAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super(FinalChallengeAdmin, self).get_urls()
        my_urls = patterns('',
                           (r'^final_challenge/$', self.final_challenge)
        )
        return my_urls + urls

    actions = ['final_challenge']

    def final_challenge(self, request, queryset):
        profiles = UserProfile.objects.filter(user__is_superuser=False).all()
        if not queryset:
            return HttpResponseRedirect('/admin')
        final_challenge = queryset[0]
        game_set = set()
        for up_player1, up_player2 in itertools.product(profiles, repeat=2):
            game_id = self.get_game_id(up_player1.pk, up_player2.pk)
            if (up_player1 == up_player2
                or not up_player1.current_bot
                or not up_player2.current_bot
                or game_id in game_set):
                continue
            challenge = Challenge()
            challenge.requested_by = up_player1
            challenge.challenger_bot = up_player1.current_bot
            challenge.challenged_bot = up_player2.current_bot
            challenge.final_challenge = final_challenge
            challenge.save()
            final_challenge.challenge_set.add(challenge)
            game_set.add(game_id)
            # dispatch the new task
            players = {up_player1.user.username: up_player1.current_bot.code,
                       up_player2.user.username: up_player2.current_bot.code,
            }
            run_match.delay(challenge.id, players)

        final_challenge.save()
        return HttpResponseRedirect('/admin')

    def get_game_id(self, x_id, y_id):
        min_id, max_id = (min(x_id, y_id), max(x_id, y_id))
        return min_id, max_id


admin.site.register(FinalChallenge, FinalChallengeAdmin)
