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


""" Imports needed to split the models in different files.

Contains the imports to the models used. It allows to not use
the file models.py and split the models in different files.
See: https://code.djangoproject.com/wiki/CookBookSplitModelsToFiles
"""

__author__ = 'Arnaud Desclouds <arnaud.software@use.startmail.com>'

from dashboard.models.ec2 import ec2_ami
from dashboard.models.ec2 import ec2_elastic_ip
from dashboard.models.ec2 import ec2_instance
from dashboard.models.ec2 import ec2_keypair
from dashboard.models.ec2 import ec2_load_balancer
from dashboard.models.ec2 import ec2_security_group
from dashboard.models.ec2 import ec2_snapshot
from dashboard.models.ec2 import ec2_tag
from dashboard.models.ec2 import ec2_volume

from dashboard.models.regions import region
from dashboard.models.regions import availability_zone

from dashboard.models.prices import ec2_price
