# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-04 00:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ashbourn', '0002_remove_activity_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='locX',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='activity',
            name='locY',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
