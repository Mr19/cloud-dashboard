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
from dashboard.models.regions.region import Region
from aws_account.models import AwsAccount

__author__ = 'Arnaud Desclouds <arnaud.software@use.startmail.com>'


class Ec2ElasticIp(models.Model):
    public_ip = models.GenericIPAddressField(primary_key=True)
    allocation_id = models.CharField(max_length=255, null=True)
    association_id = models.CharField(max_length=255, null=True)
    aws_account = models.ForeignKey(AwsAccount)
    DOMAINS = (
        ('standard', 'standard'),
        ('vpc', 'vpc')
    )
    domain = models.CharField(max_length=255,
                              choices=DOMAINS)
    instance_id = models.OneToOneField(Ec2Instance, null=True)
    network_interface_id = models.CharField(max_length=255, null=True)
    network_interface_owner_id = models.CharField(max_length=255, null=True)
    private_ip_address = models.GenericIPAddressField(null=True)
    region = models.ForeignKey(Region)
