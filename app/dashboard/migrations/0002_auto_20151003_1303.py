# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ec2instance',
            name='ec2_platform',
            field=models.CharField(max_length=255, choices=[('linux', 'linux'), ('mswin', 'mswin'), ('mswinSQL', 'mswinSQL'), ('mswinSQLWeb', 'mswinSQLWeb'), ('rhel', 'rhel'), ('sles', 'sles'), ('windows-unknown', 'windows-unknown')]),
        ),
    ]
