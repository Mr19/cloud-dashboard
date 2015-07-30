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


from django.utils.html import format_html
import django_tables2 as tables
from django_tables2.utils import A

from cloud_dashboard.common.utils.prices import compute_aws_account_daily_cost
from cloud_dashboard.common.utils.prices import compute_aws_account_hourly_cost
from cloud_dashboard.common.utils.prices import compute_aws_account_monthly_cost
from aws_account.models import AwsAccount

__author__ = 'Arnaud Desclouds <arnaud.software@use.startmail.com>'


class AwsAccountTable(tables.Table):
    aws_secret_access_key = tables.Column(accessor='aws_secret_access_key',
                                          visible=False)

    update_aws_account = tables.Column(empty_values=(),
                                       verbose_name='edit')
    delete_aws_account = tables.Column(empty_values=(),
                                       verbose_name='delete')

    hourly_cost = tables.Column(empty_values=(),
                                orderable=False,
                                verbose_name='hourly cost')
    daily_cost = tables.Column(empty_values=(),
                               orderable=False,
                               verbose_name='daily cost')
    monthly_cost = tables.Column(empty_values=(),
                                 orderable=False,
                                 verbose_name='monthly cost')

    def render_update_aws_account(self, record):
        return format_html(
            '<a href="/aws-accounts/update/{}/"><span class="glyphicon glyphicon-pencil"></span></a>',
            record.pk)

    def render_delete_aws_account(self, record):
        return format_html(
            '<a href="/aws-accounts/delete/{}/"><span class="glyphicon glyphicon-remove"></span></a>',
            record.pk)

    def render_hourly_cost(self, record):
        return '$ {}'.format(compute_aws_account_hourly_cost(record))

    def render_daily_cost(self, record):
        return '$ {}'.format(compute_aws_account_daily_cost(record))

    def render_monthly_cost(self, record):
        return '$ {}'.format(compute_aws_account_monthly_cost(record))

    class Meta:
        model = AwsAccount
        attrs = {'class': 'paleblue'}
        order_by = ('name')
        sequence = ('id',
                    'name',
                    'aws_access_key_id',
                    'hourly_cost',
                    'daily_cost',
                    'monthly_cost',
                    'update_aws_account',
                    'delete_aws_account')
