from django.contrib import admin
from tournament.models import Bot, Challenge

class BotAdmin(admin.ModelAdmin):
    list_display = ('owner', 'creation_date', 'modification_date')

class ChallengueAdmin(admin.ModelAdmin):
    list_display = ('requested_by', 'creation_date', 'winner_bot', 'challenger_bot',
        'challenged_bot')

admin.site.register(Bot, BotAdmin)
admin.site.register(Challenge, ChallengueAdmin)
