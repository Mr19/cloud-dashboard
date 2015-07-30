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

from dashboard.models.ec2.ec2_instance import Ec2Instance
from dashboard.models.ec2.ec2_tag import Ec2Tag
from dashboard.models.ec2.ec2_snapshot import Ec2Snapshot
from dashboard.models.regions.availability_zone import AvailabilityZone
from aws_account.models import AwsAccount

__author__ = 'Arnaud Desclouds <arnaud.software@use.startmail.com>'


class Ec2Volume(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    attach_time = models.DateTimeField(null=True)
    availability_zone = models.ForeignKey(AvailabilityZone, null=True)
    aws_account = models.ForeignKey(AwsAccount)
    delete_on_termination = models.BooleanField(default=False)
    instance_id = models.ForeignKey(Ec2Instance, blank=True, null=True,
                                    on_delete=models.SET_NULL)
    create_time = models.DateTimeField(null=True)
    encrypted = models.NullBooleanField(default=False)
    size = models.IntegerField(null=True)
    created_from_snapshot = models.ForeignKey(Ec2Snapshot, blank=True,
                                              null=True)
    type = models.CharField(max_length=255)
    tags = models.ManyToManyField(Ec2Tag, blank=True)
