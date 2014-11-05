# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_userprofile_code_update_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='code',
            field=models.TextField(default=b"# Example responses:\n#\n# Move to the right:\n#   return {'ACTION': 'MOVE', 'WHERE': 1}\n#\n# Move to the left:\n#   return {'ACTION': 'MOVE', 'WHERE': -1}\n#\n# Shooting projectile:\n#   return {'ACTION': 'SHOOT', 'VEL': 100, 'ANGLE': 35}\n#   # 'VEL' should be an integer > 0 and < 100\n#   # 'ANGLE' should be an integer > 0 and < 90\n#\n#\n# Do nothing:\n#   return None\n\nclass Bot(object):\n\n    def evaluate_turn(self, arena_array, feedback, life):\n        '''\n        :param arena_array:  a Python array with players location. Ie:\n        arena_array = [0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0] # (where the number is the player location)\n        :param feedback: the result of the previous turn, ie: for the move action 'SUCCESS' is returned when the enemy\n            received a hit, or 'FAILED' when missed the shot.\n        :param life: Current life level, An integer between between 0-100.\n        :return: see the comments above\n        '''\n        return None\n    ", null=True, blank=True),
            preserve_default=True,
        ),
    ]
