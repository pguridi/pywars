# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_auto_20141110_1835'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinalChallenge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(default=b'Final Challenge')),
                ('creation_date', models.DateTimeField(default=datetime.datetime(2014, 11, 10, 21, 59, 7, 562153), auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='challenge',
            name='final_challenge',
            field=models.ForeignKey(default=None, blank=True, to='game.FinalChallenge', null=True),
            preserve_default=True,
        ),
    ]
