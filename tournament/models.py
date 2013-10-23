from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save

 
class UserProfile(models.Model):
    user = models.ForeignKey(User, primary_key=True, related_name="profile")
    score = models.IntegerField('Tournament score', default=0)
    my_buffer = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        return '%s' % (self.user)

class Bot(models.Model):
    owner = models.ForeignKey(UserProfile)
    code = models.TextField()
    points = models.IntegerField(default=0)
    creation_date = models.DateTimeField(auto_now=True)
    modification_date = models.DateTimeField(auto_now=True)

    def to_dict(self):
        return {"owner": self.owner, "code": self.code}

    def __str__(self):
        return "%s - %s" % (self.owner, self.points)

    def _js_code(self):
        "Returns the person's full name."
        return self.code.replace('\n', '\\n')
    js_code = property(_js_code)

class Challenge(models.Model):
    requested_by = models.ForeignKey(User)
    creation_date = models.DateTimeField(auto_now=True)
    challenger_bot = models.ForeignKey(Bot, related_name="challenger")
    challenged_bot = models.ForeignKey(Bot, related_name="challenged")
    played = models.BooleanField(default=False)
    winner_bot = models.ForeignKey(Bot, related_name="winner", blank=True, null=True)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)

