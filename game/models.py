import json
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save


DEFAULT_BOT_CODE = """# Example responses:
#
# Move to the right:
#   return {'ACTION': 'MOVE', 'WHERE': 1}
#
# Move to the left:
#   return {'ACTION': 'MOVE', 'WHERE': -1}
#
# Shooting projectile:
#   return {'ACTION': 'SHOOT', 'VEL': 100, 'ANGLE': 35}
#   # 'VEL' should be an integer > 0 and < 100
#   # 'ANGLE' should be an integer > 0 and < 90
#
#
# Do nothing:
#   return None

class Bot(object):

    def evaluate_turn(self, arena_array, feedback, life):
        '''
        :param arena_array:  a Python array with players location. Ie:
        arena_array = [0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0] # (where the number is the player location)
        :param feedback: the result of the previous turn, ie: for the move action 'SUCCESS' is returned when the enemy
            received a hit, or 'FAILED' when missed the shot.
        :param life: Current life level, An integer between between 0-100.
        :return: see the comments above
        '''
        return None
    """

class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True, related_name="profile")
    score = models.IntegerField('Tournament score', default=0)
    code = models.TextField(default=DEFAULT_BOT_CODE, blank=True, null=True)
    code_update_date = models.DateTimeField(auto_now=True, null=True)
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

    @property
    def is_current_bot(self):
        if self.owner.current_bot == self:
            return True
        else:
            return False


class Challenge(models.Model):
    requested_by = models.ForeignKey(UserProfile)
    creation_date = models.DateTimeField(auto_now=True)
    challenger_bot = models.ForeignKey(Bot, related_name="challenger")
    challenged_bot = models.ForeignKey(Bot, related_name="challenged")
    played = models.BooleanField(default=False)
    winner_bot = models.ForeignKey(Bot, related_name="winner", blank=True, null=True)
    result = models.TextField(default='', blank=True, null=True)

    @property
    def _result(self):
        if not hasattr(self, '_result_cache') or (not getattr(self, '_result_cache', None) and self.result):
            self._result_cache = json.loads(self.result)
        return self._result_cache

    def duration(self):
        if self.result:
            return "{0:.2f}s".format(self._result['elapsed'])
        return '0s'

    def move_count(self):
        if self.result:
            return len(self._result['moves'])
        return 0

    def score(self):
        return
        #if self.result:
        #    return calc_score(self.challenger_bot, self.challenged_bot, self.winner_bot)

    def result_description(self):
        if self.result:
            return ' - '.join(['%s (%s)' % (k,v) for k,v in self._result['result']['lost'].items()])


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)