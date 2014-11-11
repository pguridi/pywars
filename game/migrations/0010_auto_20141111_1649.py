# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0009_auto_20141111_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bot',
            name='valid',
            field=models.NullBooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='finalchallenge',
            name='creation_date',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 11, 16, 49, 6, 69654), auto_now=True),
            preserve_default=True,
        ),
    ]
