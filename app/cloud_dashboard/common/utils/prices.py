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

__author__ = 'Arnaud Desclouds <arnaud.software@use.startmail.com>'


from calendar import monthrange
from datetime import date
from decimal import *

from django.db.models import Max

from dashboard.models.ec2.ec2_instance import Ec2Instance
from dashboard.models.prices.ec2_price import Ec2Price

__author__ = 'Arnaud Desclouds'


def max_resource_price():
    return Ec2Price.objects.all().aggregate(Max('hourly_price')).get(
        'hourly_price__max')


def compute_resource_price_class(resource):
    return round((
                 resource.ec2_price.hourly_price / max_resource_price()) * 10) if resource.ec2_price else None


def compute_aws_account_hourly_cost(aws_account):
    instances = Ec2Instance.objects.filter(aws_account=aws_account,
                                           state='running')
    total_cost = Decimal(0)
    for instance in instances:
        if instance.ec2_price:
            total_cost += instance.ec2_price.hourly_price
    return total_cost


def compute_aws_account_daily_cost(aws_account):
    return compute_aws_account_hourly_cost(aws_account) * Decimal(24)


def compute_aws_account_monthly_cost(aws_account, naive=True):
    if naive:
        return compute_aws_account_daily_cost(aws_account) * Decimal(30)
    else:
        return (compute_aws_account_daily_cost(aws_account) * Decimal(
            number_days_in_current_month()))


def number_days_in_current_month():
    return monthrange(date.today().year, date.today().month)[1]
