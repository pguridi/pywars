# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_auto_20141031_1747'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='code_update_date',
            field=models.DateTimeField(auto_now=True, null=True),
            preserve_default=True,
        ),
    ]
