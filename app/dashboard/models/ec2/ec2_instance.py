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

from dashboard.models.ec2.ec2_ami import Ec2Ami
from dashboard.models.ec2.ec2_tag import Ec2Tag
from dashboard.models.ec2.ec2_keypair import Ec2Keypair
from dashboard.models.ec2.ec2_security_group import Ec2SecurityGroup
from dashboard.models.regions.availability_zone import AvailabilityZone
from aws_account.models import AwsAccount
from dashboard.models.prices.ec2_price import Ec2Price

__author__ = 'Arnaud Desclouds <arnaud.software@use.startmail.com>'


class Ec2Instance(models.Model):
    id = models.CharField(primary_key=True, max_length=10)

    architecture = models.CharField(max_length=255)
    availability_zone = models.ForeignKey(AvailabilityZone, null=True)
    aws_account = models.ForeignKey(AwsAccount)

    EC2_PLATFORMS = (
        ('linux', 'linux'),
        ('mswin', 'mswin'),
        ('mswinSQL', 'mswinSQL'),
        ('mswinSQLWeb', 'mswinSQLWeb'),
        ('rhel', 'rhel'),
        ('sles', 'sles'),
        ('windows-unknown', 'windows-unknown')
    )
    ec2_platform = models.CharField(max_length=255, choices=EC2_PLATFORMS)
    ec2_price = models.ForeignKey(Ec2Price, null=True)
    key_name = models.ForeignKey(Ec2Keypair, blank=True, null=True)
    image_id = models.ForeignKey(Ec2Ami, default=None, null=True)
    INSTANCE_TYPES = (
        ('t2.micro', 't2.micro'),
        ('t2.small', 't2.small'),
        ('t2.medium', 't2.medium'),
        ('m3.medium', 'm3.medium'),
        ('m3.large', 'm3.large'),
        ('m3.xlarge', 'm3.xlarge'),
        ('m3.2xlarge', 'm3.2xlarge'),
        ('c4.large', 'c4.large'),
        ('c4.xlarge', 'c4.xlarge'),
        ('c4.2xlarge', 'c4.2xlarge'),
        ('c4.4xlarge', 'c4.4xlarge'),
        ('c4.8xlarge', 'c4.8xlarge'),
        ('c3.large', 'c3.large'),
        ('c3.xlarge', 'c3.xlarge'),
        ('c3.2xlarge', 'c3.2xlarge'),
        ('c3.4xlarge', 'c3.4xlarge'),
        ('c3.8xlarge', 'c3.8xlarge'),
        ('g2.2xlarge', 'g2.2xlarge'),
        ('r3.large', 'r3.large'),
        ('r3.xlarge', 'r3.xlarge'),
        ('r3.2xlarge', 'r3.2xlarge'),
        ('r3.4xlarge', 'r3.4xlarge'),
        ('r3.8xlarge', 'r3.8xlarge'),
        ('i2.xlarge', 'i2.xlarge'),
        ('i2.2xlarge', 'i2.2xlarge'),
        ('i2.4xlarge', 'i2.4xlarge'),
        ('i2.8xlarge', 'i2.8xlarge'),
        ('d2.xlarge', 'd2.xlarge'),
        ('d2.2xlarge', 'd2.2xlarge'),
        ('d2.4xlarge', 'd2.4xlarge'),
        ('d2.8xlarge', 'd2.8xlarge')
    )
    instance_type = models.CharField(max_length=255,
                                     choices=INSTANCE_TYPES)
    kernel = models.CharField(max_length=255, null=True)
    launch_time = models.DateTimeField()
    platform = models.CharField(max_length=255, null=True)
    public_dns_name = models.CharField(max_length=255, null=True)
    security_groups = models.ManyToManyField(Ec2SecurityGroup)
    STATES = (
        ('pending', 'pending'),
        ('running', 'running'),
        ('shutting-down', 'shutting-down'),
        ('terminated', 'terminated'),
        ('stopping', 'stopping'),
        ('stopped', 'stopped')
    )
    state = models.CharField(max_length=255,
                             choices=STATES)
    tags = models.ManyToManyField(Ec2Tag, blank=True)


    def has_tags(self):
        return self.tags.all().exists()

    def get_tags(self):
        return self.tags.all()
