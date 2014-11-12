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
            model_name='bot',
            name='valid',
            field=models.CharField(default=b'PENDING', max_length=10, choices=[(b'READY', b'Ready'), (b'PENDING', b'Pending'), (b'INVALID', b'Invalid')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='finalchallenge',
            name='creation_date',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 12, 12, 43, 47, 948044), auto_now=True),
            preserve_default=True,
        ),
    ]
