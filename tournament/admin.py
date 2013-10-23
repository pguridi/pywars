from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from tournament.models import Bot, Challengue, UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'score')
    model = UserProfile

class UserProfileInline(admin.TabularInline):
    model = UserProfile

class UserWithProfileAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ( 'email', 'username')

class BotAdmin(admin.ModelAdmin):
    list_display = ('owner', 'creation_date', 'modification_date')

class ChallengueAdmin(admin.ModelAdmin):
    list_display = ('requested_by', 'creation_date', 'winner_bot', 'challenguer_bot',
        'challengued_bot')

admin.site.register(Bot, BotAdmin)
admin.site.register(Challengue, ChallengueAdmin)
admin.site.unregister(User)
admin.site.register(User, UserWithProfileAdmin)

admin.site.register(UserProfile, UserProfileAdmin)
