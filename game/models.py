#-*-coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
import os
from game.tasks import run_match
from datetime import datetime


sample_bot_location = os.path.join(settings.PROJECT_ROOT, 'game_engine', 'default_user_bot.py')

DEFAULT_BOT_CODE = ''
with open(sample_bot_location, 'r') as f:
    DEFAULT_BOT_CODE = f.read()


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
                    (Q(canceled=False) & Q(challenger_bot__owner=self) & Q(challenged_bot__owner=other_prof)) |
                    (Q(canceled=False) & Q(challenged_bot__owner=self) & Q(challenger_bot__owner=other_prof))
                ).latest('creation_date').pk
        except ObjectDoesNotExist:
            return None

    @property
    def points(self):
        win_matches = Challenge.objects.filter(final_challenge__isnull = False, winner_player = self).count()
        ties = Challenge.objects.filter((Q(draw_player1 = self) | Q(draw_player2 = self)), final_challenge__isnull = False).count()
        return (3 * win_matches) + ties

    @property
    def win(self):
        win_matches = Challenge.objects.filter(final_challenge__isnull=False, winner_player=self).count()
        return (float(win_matches) / self.finalmatches) * 100

    @property
    def finalmatches(self):
        final = Challenge.objects.filter(Q(challenger_bot__owner=self) | Q(challenged_bot__owner=self)).count()
        return float(final)

    @property
    def lost(self):
        lost = Challenge.objects.filter(final_challenge__isnull = False, loser_player=self).count()
        return (float(lost) / self.finalmatches) * 100

    @property
    def timedout(self):
        timedout = Challenge.objects.filter(Q(challenger_bot__owner=self) | Q(challenged_bot__owner=self) & Q(final_challenge__isnull=False) & Q (canceled=True)).count()
        return (float(timedout) / self.finalmatches) * 100

    @property
    def tie(self):
        ties = Challenge.objects.filter((Q(draw_player1 = self) | Q(draw_player2 = self)), final_challenge__isnull = False).count()
        return (float(ties) / self.finalmatches) * 100


class Bot(models.Model):
    READY, PENDING, INVALID = 'READY', 'PENDING', 'INVALID'
    STATUS_CHOICES = (
        (READY, 'Ready'),
        (PENDING, 'Pending'),
        (INVALID, 'Invalid'),
    )
    owner = models.ForeignKey(UserProfile)
    code = models.TextField()
    creation_date = models.DateTimeField(auto_now=True)
    modification_date = models.DateTimeField(auto_now=True)
    valid = models.CharField(max_length=10,
                             choices=STATUS_CHOICES,
                             default=PENDING)
    invalid_reason = models.TextField(null=True, default='')
    
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


class FinalChallenge(models.Model):
    description = models.TextField(default='Final Challenge', null=False)
    creation_date = models.DateTimeField(auto_now=True, default=datetime.now())


class Challenge(models.Model):
    requested_by = models.ForeignKey(UserProfile)
    creation_date = models.DateTimeField(auto_now=True)
    challenger_bot = models.ForeignKey(Bot, related_name="challenger")
    challenged_bot = models.ForeignKey(Bot, related_name="challenged")
    played = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)
    winner_bot = models.ForeignKey(Bot, related_name="winner", blank=True, null=True)
    winner_player = models.ForeignKey(UserProfile, related_name="winner_player", blank=True, null=True)
    loser_player = models.ForeignKey(UserProfile, related_name="loser_player", blank=True, null=True)
    draw_player1 = models.ForeignKey(UserProfile, related_name="draw_player1", blank=True, null=True)
    draw_player2 = models.ForeignKey(UserProfile, related_name="draw_playe2", blank=True, null=True)
    result = models.TextField(default='', blank=True, null=True)
    elapsed_time = models.TextField(null=True)
    final_challenge = models.ForeignKey(FinalChallenge, blank=True, null=True, default=None)
    information = models.TextField(default='', null=False)

    def result_description(self):
        if self.result:
            return 'Result description..'

    def __unicode__(self):
        return u'{} vs. {} [{}]'.format(self.challenger_bot.owner.user.username,
                                        self.challenged_bot.owner.user.username,
                                        self.creation_date.strftime("%a %d-%H:%M:%S"))
    def __str__(self):
        return self.__unicode__()

    def _resolve_players(self, p1, p2):
        _win_tmp = u"{} ♛"
        if not self.winner_player:
            return p1, "{} - [DRAW]".format(p2)
        if "CRASHED" in self.information.upper() or "INVALID OUTPUT" in self.information.upper():
            if self.loser_player.user.username == p1:
                return "{} &#9760;".format(p1), _win_tmp.format(p2)
            else:
                return _win_tmp.format(p1), "{} &#9760;".format(p2)
                
        if self.winner_player.user.username == p1:
            return _win_tmp.format(p1), p2
        if self.winner_player.user.username == p2:
            return p1, _win_tmp.format(p2)

    def caption(self):
        first, second = self._resolve_players(
            self.challenger_bot.owner.user.username,
            self.challenged_bot.owner.user.username
        )
        return u'{first} <-> {second}'.format(first=first, second=second)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


def dispatch_challengue(sender, instance, created, **kwargs):
    if created:
        players = {instance.challenger_bot.owner.user.username: instance.challenger_bot.code,
                   instance.challenged_bot.owner.user.username: instance.challenged_bot.code}
        run_match.delay(instance.id, players)


post_save.connect(create_user_profile, sender=User)
post_save.connect(dispatch_challengue, sender=Challenge)
