# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.TextField()),
                ('creation_date', models.DateTimeField(auto_now=True)),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('valid', models.CharField(default=b'PENDING', max_length=10, choices=[(b'READY', b'Ready'), (b'PENDING', b'Pending'), (b'INVALID', b'Invalid')])),
                ('invalid_reason', models.TextField(default=b'', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateTimeField(auto_now=True)),
                ('played', models.BooleanField(default=False)),
                ('canceled', models.BooleanField(default=False)),
                ('result', models.TextField(default=b'', null=True, blank=True)),
                ('elapsed_time', models.TextField(null=True)),
                ('information', models.TextField(default=b'')),
                ('challenged_bot', models.ForeignKey(related_name='challenged', to='game.Bot')),
                ('challenger_bot', models.ForeignKey(related_name='challenger', to='game.Bot')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FinalChallenge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(default=b'Final Challenge')),
                ('creation_date', models.DateTimeField(default=datetime.datetime(2014, 11, 13, 17, 47, 51, 992002), auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(related_name='profile', primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('score', models.IntegerField(default=0, verbose_name=b'Tournament score')),
                ('code', models.TextField(default=b"# Example responses:\n#\n# Move to the right:\n#   return {'ACTION': 'MOVE', 'WHERE': 1}\n#\n# Move to the left:\n#   return {'ACTION': 'MOVE', 'WHERE': -1}\n#\n# Shooting projectile:\n#   return {'ACTION': 'SHOOT', 'VEL': 100, 'ANGLE': 35}\n#   # 'VEL' should be an integer x, 0 < x < 50\n#   # 'ANGLE' should be an integer x, 10 <= x < 90\n#\n#\n# Do nothing:\n#   return None\n\nclass Bot(object):\n\n    def evaluate_turn(self, feedback, life):\n        '''\n        :param feedback: (dict) the result of the previous turn,\n            ie: for the move action 'SUCCESS' is returned when the enemy\n            received a hit, or 'FAILED' when missed the shot.\n        {'RESULT': 'SUCCESS' | 'FAILED', Result of the action\n         'POSITION': (x, y) | None, In case of move success, or at start\n         'MISSING': 'HOT' | 'WARM' | 'COLD' | None, Depending how close the last\n         impact was, if applicable }\n        :param life: Current life level, An integer between between 0-100.\n        :return: see the comments above\n        '''\n        return None\n", null=True, blank=True)),
                ('code_update_date', models.DateTimeField(auto_now=True, null=True)),
                ('current_bot', models.ForeignKey(related_name='current_profile', blank=True, to='game.Bot', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='challenge',
            name='draw_player1',
            field=models.ForeignKey(related_name='draw_player1', blank=True, to='game.UserProfile', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='challenge',
            name='draw_player2',
            field=models.ForeignKey(related_name='draw_playe2', blank=True, to='game.UserProfile', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='challenge',
            name='final_challenge',
            field=models.ForeignKey(default=None, blank=True, to='game.FinalChallenge', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='challenge',
            name='loser_player',
            field=models.ForeignKey(related_name='loser_player', blank=True, to='game.UserProfile', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='challenge',
            name='requested_by',
            field=models.ForeignKey(to='game.UserProfile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='challenge',
            name='winner_bot',
            field=models.ForeignKey(related_name='winner', blank=True, to='game.Bot', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='challenge',
            name='winner_player',
            field=models.ForeignKey(related_name='winner_player', blank=True, to='game.UserProfile', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bot',
            name='owner',
            field=models.ForeignKey(to='game.UserProfile'),
            preserve_default=True,
        ),
    ]
