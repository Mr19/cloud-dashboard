# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AwsAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('aws_access_key_id', models.CharField(max_length=255)),
                ('aws_secret_access_key', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='AwsUser',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('resources_update_interval', models.IntegerField(default=60)),
                ('resources_last_updated', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc))),
                ('prices_last_updated', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc))),
                ('aws_accounts', models.ManyToManyField(to='aws_account.AwsAccount', blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
