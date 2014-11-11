# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0010_auto_20141111_1649'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='information',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='finalchallenge',
            name='creation_date',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 11, 19, 42, 51, 355874), auto_now=True),
            preserve_default=True,
        ),
    ]
