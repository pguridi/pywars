# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.TextField()),
                ('creation_date', models.DateTimeField(auto_now=True)),
                ('modification_date', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateTimeField(auto_now=True)),
                ('played', models.BooleanField(default=False)),
                ('result', models.TextField(default=b'', null=True, blank=True)),
                ('challenged_bot', models.ForeignKey(related_name='challenged', to='game.Bot')),
                ('challenger_bot', models.ForeignKey(related_name='challenger', to='game.Bot')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(related_name='profile', primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('score', models.IntegerField(default=0, verbose_name=b'Tournament score')),
                ('my_buffer', models.TextField(default=b"import random\nclass MyLightCycleBot(LightCycleBaseBot):\n\n    def get_next_step(self, arena, x, y, direction):\n        # arena.shape[0] is the arena width\n        # arena.shape[1] is the arena height\n        # arena[x,y] is your current position\n        return random.choice(['N','W','E','S'])\n    ", null=True, blank=True)),
                ('current_bot', models.ForeignKey(related_name='current_profile', blank=True, to='game.Bot', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='challenge',
            name='requested_by',
            field=models.ForeignKey(to='game.UserProfile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='challenge',
            name='winner_bot',
            field=models.ForeignKey(related_name='winner', blank=True, to='game.Bot', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bot',
            name='owner',
            field=models.ForeignKey(to='game.UserProfile'),
            preserve_default=True,
        ),
    ]
