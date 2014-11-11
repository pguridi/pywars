# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0007_auto_20141110_2159'),
    ]

    operations = [
        migrations.AddField(
            model_name='bot',
            name='invalid_reason',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bot',
            name='valid',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='finalchallenge',
            name='creation_date',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 11, 16, 31, 15, 190786), auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='code',
            field=models.TextField(default=b"# Example responses:\n#\n# Move to the right:\n#   return {'ACTION': 'MOVE', 'WHERE': 1}\n#\n# Move to the left:\n#   return {'ACTION': 'MOVE', 'WHERE': -1}\n#\n# Shooting projectile:\n#   return {'ACTION': 'SHOOT', 'VEL': 100, 'ANGLE': 35}\n#   # 'VEL' should be an integer x, 0 < x < 50\n#   # 'ANGLE' should be an integer x, 10 <= x < 90\n#\n#\n# Do nothing:\n#   return None\n\nclass Bot(object):\n\n    def evaluate_turn(self, feedback, life):\n        '''\n        :param feedback: (dict) the result of the previous turn,\n            ie: for the move action 'SUCCESS' is returned when the enemy\n            received a hit, or 'FAILED' when missed the shot.\n        {'RESULT': 'SUCCESS' | 'FAILED', Result of the action\n         'POSITION': (x, y) | None, In case of move success, or at start\n         'MISSING': 'HOT' | 'WARM' | 'COLD' | None, Depending how close the last\n         impact was, if applicable }\n        :param life: Current life level, An integer between between 0-100.\n        :return: see the comments above\n        '''\n        return None\n", null=True, blank=True),
            preserve_default=True,
        ),
    ]
