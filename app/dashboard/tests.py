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


import datetime

from django.test import TestCase
from django.utils import timezone

from dashboard.models.ec2.ec2_instance import Ec2Instance

__author__ = 'Arnaud Desclouds <arnaud.software@use.startmail.com>'


class InstanceCreationTests(TestCase):
    nb_instances = 4

    @classmethod
    def setUpTestData(cls):
        for i in range(cls.nb_instances):
            Ec2Instance.objects.create(
                id=i,
                instance_type=Ec2Instance.INSTANCE_TYPES[
                    (i % len(Ec2Instance.INSTANCE_TYPES))][0],
                state=Ec2Instance.STATES[(i % len(Ec2Instance.STATES))][0],
                launch_time=datetime.datetime.now(timezone.utc),
                aws_account_id=42)

    def test_number_instances(self):
        self.assertEqual(len(Ec2Instance.objects.all()), self.nb_instances)
