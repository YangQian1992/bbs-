# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-08-15 07:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog01', '0004_auto_20180815_1513'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='artcleupdown',
            options={'verbose_name': ('点赞',), 'verbose_name_plural': ('点赞',)},
        ),
    ]