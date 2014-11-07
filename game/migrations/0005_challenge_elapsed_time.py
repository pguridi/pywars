# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_auto_20141103_2032'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='elapsed_time',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
    ]
