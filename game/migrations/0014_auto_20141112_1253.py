# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0013_auto_20141112_1253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bot',
            name='invalid_reason',
            field=models.TextField(default=b'pending', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='finalchallenge',
            name='creation_date',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 12, 12, 53, 34, 749456), auto_now=True),
            preserve_default=True,
        ),
    ]
