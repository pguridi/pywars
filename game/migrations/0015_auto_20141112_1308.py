# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0014_auto_20141112_1253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='finalchallenge',
            name='creation_date',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 12, 13, 8, 48, 466513), auto_now=True),
            preserve_default=True,
        ),
    ]
