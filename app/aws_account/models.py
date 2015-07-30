# The MIT License (MIT)
#
# Copyright (c) 2015 Haute École d'Ingénierie et de Gestion du Canton de Vaud
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from django.db import models
from django.contrib.auth.models import User
import datetime
from datetime import timezone

__author__ = 'Arnaud Desclouds <arnaud.software@use.startmail.com>'


class AwsAccount(models.Model):
    name = models.CharField(max_length=255)
    aws_access_key_id = models.CharField(max_length=255)
    aws_secret_access_key = models.CharField(max_length=255)


class AwsUser(models.Model):
    user = models.OneToOneField(User)
    aws_accounts = models.ManyToManyField(AwsAccount, blank=True)
    resources_update_interval = models.IntegerField(default=60)  # 60 minutes
    resources_last_updated = models.DateTimeField(
        default=datetime.datetime(1970, month=1, day=1, tzinfo=timezone.utc))

    prices_update_interval = datetime.timedelta(days=7)  # 7 days
    prices_last_updated = models.DateTimeField(
        default=datetime.datetime(1970, month=1, day=1, tzinfo=timezone.utc))

    def resources_up_to_date(self):
        return (
            datetime.datetime.now(timezone.utc) - self.resources_last_updated
            < datetime.timedelta(minutes=self.resources_update_interval))

    def prices_up_to_date(self):
        return (datetime.datetime.now(timezone.utc) - self.prices_last_updated
                < self.prices_update_interval)
