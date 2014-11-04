from django.contrib import admin

# Register your models here.

from game.models import Bot, Challenge, UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    pass
admin.site.register(UserProfile, UserProfileAdmin)

class BotAdmin(admin.ModelAdmin):
    pass
admin.site.register(Bot, BotAdmin)

class ChallengeAdmin(admin.ModelAdmin):
    pass
admin.site.register(Challenge, ChallengeAdmin)