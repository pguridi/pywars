# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='my_buffer',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='code',
            field=models.TextField(default=b"import random\nclass MyTankBot(BattlegroundBaseBot):\n\n    def get_next_step(self, arena, x, y, direction):\n        # arena.shape[0] is the arena width\n        # arena.shape[1] is the arena height\n        # arena[x,y] is your current position\n        return random.choice(['N','W','E','S'])\n    ", null=True, blank=True),
            preserve_default=True,
        ),
    ]
