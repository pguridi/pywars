import json
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save

DEFAULT_BOT_CODE = """import random
class MyLightCycleBot(LightCycleBaseBot):

    def get_next_step(self, arena, x, y, direction):
        # arena.shape[0] is the arena width
        # arena.shape[1] is the arena height
        # arena[x,y] is your current position
        return random.choice(['N','W','E','S'])
    """

class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True, related_name="profile")
    score = models.IntegerField('Tournament score', default=0)
    my_buffer = models.TextField(default=DEFAULT_BOT_CODE, blank=True, null=True)
    current_bot = models.ForeignKey('Bot', related_name="current_profile", blank=True, null=True)

    def __str__(self):
        return '%s' % (self.user)

    def latest_match_id(self, other_prof):
        try:
            if other_prof != self:
                return Challenge.objects.filter(
                    (Q(challenger_bot__owner=self) & Q(challenged_bot__owner=other_prof)) |
                    (Q(challenged_bot__owner=self) & Q(challenger_bot__owner=other_prof))
                ).latest('creation_date').pk
        except ObjectDoesNotExist:
            return None


class Bot(models.Model):
    owner = models.ForeignKey(UserProfile)
    code = models.TextField()
    creation_date = models.DateTimeField(auto_now=True)
    modification_date = models.DateTimeField(auto_now=True)

    def to_dict(self):
        return {"owner": self.owner, "code": self.code}

    def __str__(self):
        return "%s - %s" % (self.owner, self.creation_date)

    def _is_current_bot(self):
        if self.owner.current_bot == self:
            return True
        else:
            return False
    is_current_bot = property(_is_current_bot)

    def _js_code(self):
        "Returns the person's full name."
        return self.code.replace('\n', '\\n')
    js_code = property(_js_code)


class Challenge(models.Model):
    requested_by = models.ForeignKey(UserProfile)
    creation_date = models.DateTimeField(auto_now=True)
    challenger_bot = models.ForeignKey(Bot, related_name="challenger")
    challenged_bot = models.ForeignKey(Bot, related_name="challenged")
    played = models.BooleanField(default=False)
    winner_bot = models.ForeignKey(Bot, related_name="winner", blank=True, null=True)
    result = models.TextField(default='', blank=True, null=True)

    def get_duration_match(self):
        res = "{0:.2f}".format(json.loads(self.result)['elapsed']) + 's'
        return res


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)
