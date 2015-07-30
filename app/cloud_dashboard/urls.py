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


from django.conf.urls import include, url
from django.contrib import admin

from dashboard.views import HomePageView
from dashboard.views import Ec2AmiTableView
from dashboard.views import Ec2ElasticIpTableView
from dashboard.views import Ec2KeypairTableView
from dashboard.views import Ec2InstanceTableView
from dashboard.views import Ec2LoadBalancerTableView
from dashboard.views import Ec2SecurityGroupTableView
from dashboard.views import Ec2SnapshotTableView
from dashboard.views import Ec2TagTableView
from dashboard.views import Ec2VolumeTableView
from dashboard.views import change_state_ec2_instances_view
from dashboard.views import change_state_ec2_volumes_view
from aws_account.views import create_aws_account_view
from aws_account.views import delete_aws_account_view
from aws_account.views import create_user
from aws_account.views import logout_view
from aws_account.views import AwsAccountUpdate
from aws_account.views import AwsAccountTableView

__author__ = 'Arnaud Desclouds <arnaud.software@use.startmail.com>'

urlpatterns = [
    url(r'^$', HomePageView.as_view(), name='home'),


    url(r'^admin/', include(admin.site.urls)),
    url(r'^ec2amis/$', Ec2AmiTableView.as_view()),
    url(r'^ec2elasticips/$', Ec2ElasticIpTableView.as_view(),
        name='Ec2ElasticIpTableView'),
    url(r'^ec2keypairs/$', Ec2KeypairTableView.as_view(),
        name='Ec2KeypairTableView'),
    url(r'^ec2instances/$', Ec2InstanceTableView.as_view(),
        name='Ec2InstanceTableView'),
    url(r'^ec2loadbalancers/$', Ec2LoadBalancerTableView.as_view(),
        name='Ec2LoadBalancerTableView'),
    url(r'^ec2securitygroups/$', Ec2SecurityGroupTableView.as_view(),
        name='Ec2SecurityGroupTableView'),
    url(r'^ec2snapshots/$', Ec2SnapshotTableView.as_view(),
        name='Ec2SnapshotTableView'),
    url(r'^ec2tags/$', Ec2TagTableView.as_view(),
        name='Ec2TagTableView'),
    url(r'^ec2volumes/$', Ec2VolumeTableView.as_view(),
        name='ec2volumesTableView'),
    url(r'^logout/', logout_view),
    url('^', include('django.contrib.auth.urls'), ),
    url('^django-rq/', include('django_rq.urls'), ),
    url(r'^sign-up/', create_user),
    url(r'^aws-accounts/$', AwsAccountTableView.as_view()),
    url(r'aws-accounts/add/$',
        create_aws_account_view,
        name='aws_account_add'),
    url(r'aws-accounts/update/(?P<pk>.*?)/$',
        AwsAccountUpdate.as_view(success_url='/aws-accounts/'),
        name='aws_account_update'),
    url(r'aws-accounts/delete/(?P<pk>.*?)/$',
        delete_aws_account_view,
        name='aws_account_delete'),
    url(r'^stop-ec2-instances/$', change_state_ec2_instances_view),
    url(r'^manage-ec2-volumes/$', change_state_ec2_volumes_view),
]
