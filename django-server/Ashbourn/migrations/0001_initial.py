# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-28 04:57
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner', models.CharField(default='P', max_length=1)),
                ('category', models.CharField(default='not specified', max_length=20)),
                ('time', models.DateTimeField()),
                ('activity_type', models.CharField(max_length=100)),
                ('activity_data', models.TextField(blank=True, default='')),
            ],
            options={
                'verbose_name': 'Activity',
                'verbose_name_plural': 'Activities',
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=50)),
                ('address', models.CharField(max_length=30)),
                ('geofence', models.CharField(max_length=80)),
                ('description', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('watch_id', models.CharField(max_length=20)),
                ('tag_id', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=50)),
                ('cell_number', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')])),
                ('hash', models.CharField(blank=True, max_length=10, null=True, unique=True)),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='Ashbourn.Location')),
            ],
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relation_type', models.CharField(max_length=20)),
                ('person_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relations', to='Ashbourn.Person')),
                ('person_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ashbourn.Person')),
            ],
        ),
        migrations.AddField(
            model_name='activity',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Ashbourn.Location'),
        ),
        migrations.AddField(
            model_name='activity',
            name='person',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='Ashbourn.Person'),
        ),
    ]