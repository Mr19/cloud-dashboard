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

__author__ = 'Arnaud Desclouds <arnaud.software@use.startmail.com>'


class Region(models.Model):
    """
        EC2 Regions.

        See: https://docs.aws.amazon.com/general/latest/gr/rande.html#ec2_region
    """
    REGION_NAMES = (
        ('us-east-1', 'US East (N. Virginia)'),
        ('us-west-2', 'US West (Oregon)'),
        ('us-west-1', 'US West (N. California)'),
        ('eu-west-1', 'EU (Ireland)'),
        ('eu-central-1', 'EU (Frankfurt)'),
        ('ap-southeast-1', 'Asia Pacific (Singapore)'),
        ('ap-southeast-2', 'Asia Pacific (Sydney)'),
        ('ap-northeast-1', 'Asia Pacific (Tokyo)'),
        ('sa-east-1', 'South America (Sao Paulo)')
    )
    region_name = models.CharField(primary_key=True,
                                   max_length=255,
                                   choices=REGION_NAMES)

    class Meta:
        ordering = ['region_name']
