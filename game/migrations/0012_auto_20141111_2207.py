# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0011_auto_20141111_1942'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='challenge',
            name='information',
        ),
        migrations.AlterField(
            model_name='finalchallenge',
            name='creation_date',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 11, 22, 7, 18, 712008), auto_now=True),
            preserve_default=True,
        ),
    ]
