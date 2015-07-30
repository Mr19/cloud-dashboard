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


import time

from django.views.generic import TemplateView
from django_tables2 import SingleTableView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect

from dashboard.models.ec2.ec2_ami import Ec2Ami
from dashboard.models.ec2.ec2_elastic_ip import Ec2ElasticIp
from dashboard.models.ec2.ec2_keypair import Ec2Keypair
from dashboard.models.ec2.ec2_instance import Ec2Instance
from dashboard.models.ec2.ec2_load_balancer import Ec2LoadBalancer
from dashboard.models.ec2.ec2_security_group import Ec2SecurityGroup
from dashboard.models.ec2.ec2_snapshot import Ec2Snapshot
from dashboard.models.ec2.ec2_tag import Ec2Tag
from dashboard.models.ec2.ec2_volume import Ec2Volume
from dashboard.tables import Ec2AmiTable
from dashboard.tables import Ec2ElasticIpTable
from dashboard.tables import Ec2KeypairTable
from dashboard.tables import Ec2InstanceTable
from dashboard.tables import Ec2LoadBalancerTable
from dashboard.tables import Ec2SecurityGroupTable
from dashboard.tables import Ec2SnapshotTable
from dashboard.tables import Ec2TagTable
from dashboard.tables import Ec2VolumeTable
from dashboard.vendor.aws_resources_controller import AwsResourcesController
from aws_account.models import AwsUser

__author__ = 'Arnaud Desclouds <arnaud.software@use.startmail.com>'


def change_state_ec2_instances_view(request):
    if request.method == 'POST':
        pks = request.POST.getlist('selected_ec2instance')
        if pks:
            new_state = ''
            if 'stop-ec2-instances' in request.POST:
                new_state = 'stopped'
            elif 'terminate-ec2-instances' in request.POST:
                new_state = 'terminated'
            selected_ec2_instances = (Ec2Instance.objects.filter(pk__in=pks))

            ec2_instances_changed_pks = [i.id for i in AwsResourcesController(
                request.user).change_state_ec2_instances(selected_ec2_instances,
                                                         new_state)]

            ec2_instances_changed = Ec2Instance.objects.filter(
                pk__in=ec2_instances_changed_pks)
            for ec2_instance in ec2_instances_changed:
                if new_state == 'terminated':
                    # Call list() to avoid lazy-loading
                    volumes_to_delete = list(ec2_instance.ec2volume_set.filter(delete_on_termination=True))
                    ec2_instance.delete()
                    # Wait for volume detachment
                    time.sleep(15)
                    ec2_volumes_deleted_pks = AwsResourcesController(request.user).change_state_ec2_volumes(volumes_to_delete, 'deleted')
                    ec2_volumes_deleted = Ec2Volume.objects.filter(
                                                pk__in=ec2_volumes_deleted_pks)
                    for ec2_volume in ec2_volumes_deleted:
                        ec2_volume.delete()
                elif new_state == 'stopped':
                    ec2_instance.state = new_state
                    ec2_instance.public_dns_name = ''
                    ec2_instance.save()


        return HttpResponseRedirect('/ec2instances/')


def change_state_ec2_volumes_view(request):
    if request.method == 'POST':
        pks = request.POST.getlist('selected_ec2volume')
        if pks:
            new_state = ''
            if 'detach-ec2-volumes' in request.POST:
                new_state = 'detached'
            elif 'delete-ec2-volumes' in request.POST:
                new_state = 'deleted'

            selected_ec2_volumes = (Ec2Volume.objects.filter(pk__in=pks))

            ec2_volumes_changed_pks = AwsResourcesController(
                request.user).change_state_ec2_volumes(selected_ec2_volumes,
                                                       new_state)

            ec2_volumes_changed = Ec2Volume.objects.filter(
                pk__in=ec2_volumes_changed_pks)
            if ec2_volumes_changed:
                if new_state == 'detached':
                    for ec2_volume in ec2_volumes_changed:
                        ec2_volume.attach_time = None
                        ec2_volume.instance_id = None
                        ec2_volume.save()
                elif new_state == 'deleted':
                    for ec2_volume in ec2_volumes_changed:
                        ec2_volume.delete()

        return HttpResponseRedirect('/ec2volumes/')


class HomePageView(TemplateView):
    template_name = "home.html"


# https://django-tables2.readthedocs.org/en/latest/pages/generic-mixins.html
class Ec2AmiTableView(SingleTableView):
    model = Ec2Ami
    table_class = Ec2AmiTable

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Ec2AmiTableView, self).dispatch(*args, **kwargs)

    def get_table_data(self):
        AwsResourcesController(self.request.user).load_ec2_data()
        current_accounts = AwsUser.objects.get(
            user=self.request.user).aws_accounts.all()
        return Ec2Ami.objects.filter(aws_account__in=current_accounts)

    def get_context_data(self, **kwargs):
        context = super(Ec2AmiTableView, self).get_context_data(**kwargs)
        context['instance_id'] = self.request.GET.get('instance_id')
        context['tag_id'] = self.request.GET.get('tag_id')
        return context


class Ec2ElasticIpTableView(SingleTableView):
    model = Ec2ElasticIp
    table_class = Ec2ElasticIpTable

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Ec2ElasticIpTableView, self).dispatch(*args, **kwargs)

    def get_table_data(self):
        AwsResourcesController(self.request.user).load_ec2_data()
        current_accounts = AwsUser.objects.get(
            user=self.request.user).aws_accounts.all()
        return Ec2ElasticIp.objects.filter(aws_account__in=current_accounts)

    def get_context_data(self, **kwargs):
        context = super(Ec2ElasticIpTableView, self).get_context_data(**kwargs)
        context['instance_id'] = self.request.GET.get('instance_id')
        return context


class Ec2InstanceTableView(SingleTableView):
    model = Ec2Instance
    table_class = Ec2InstanceTable

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Ec2InstanceTableView, self).dispatch(*args, **kwargs)

    def get_table_data(self):
        AwsResourcesController(self.request.user).load_ec2_data()
        current_accounts = AwsUser.objects.get(
            user=self.request.user).aws_accounts.all()
        return Ec2Instance.objects.filter(aws_account__in=current_accounts)

    def get_context_data(self, **kwargs):
        context = super(Ec2InstanceTableView, self).get_context_data(**kwargs)
        context['ami_id'] = self.request.GET.get('ami_id')
        context['elasticip_id'] = self.request.GET.get('elasticip_id')
        context['keypair_id'] = self.request.GET.get('keypair_id')
        context['loadbalancer_id'] = self.request.GET.get('loadbalancer_id')
        context['securitygroup_id'] = self.request.GET.get('securitygroup_id')
        context['tag_id'] = self.request.GET.get('tag_id')
        context['volume_id'] = self.request.GET.get('volume_id')
        return context


class Ec2KeypairTableView(SingleTableView):
    model = Ec2Keypair
    table_class = Ec2KeypairTable

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Ec2KeypairTableView, self).dispatch(*args, **kwargs)

    def get_table_data(self):
        AwsResourcesController(self.request.user).load_ec2_data()
        current_accounts = AwsUser.objects.get(
            user=self.request.user).aws_accounts.all()
        return Ec2Keypair.objects.filter(aws_account__in=current_accounts)

    def get_context_data(self, **kwargs):
        context = super(Ec2KeypairTableView, self).get_context_data(**kwargs)
        context['instance_id'] = self.request.GET.get('instance_id')
        return context


class Ec2LoadBalancerTableView(SingleTableView):
    model = Ec2LoadBalancer
    table_class = Ec2LoadBalancerTable

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Ec2LoadBalancerTableView, self).dispatch(*args, **kwargs)

    def get_table_data(self):
        AwsResourcesController(self.request.user).load_ec2_data()
        current_accounts = AwsUser.objects.get(
            user=self.request.user).aws_accounts.all()
        return Ec2LoadBalancer.objects.filter(aws_account__in=current_accounts)

    def get_context_data(self, **kwargs):
        context = super(Ec2LoadBalancerTableView, self).get_context_data(**kwargs)
        context['instance_id'] = self.request.GET.get('instance_id')
        context['securitygroup_id'] = self.request.GET.get('securitygroup_id')
        return context


class Ec2SecurityGroupTableView(SingleTableView):
    model = Ec2SecurityGroup
    table_class = Ec2SecurityGroupTable

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Ec2SecurityGroupTableView, self).dispatch(*args, **kwargs)

    def get_table_data(self):
        AwsResourcesController(self.request.user).load_ec2_data()
        current_accounts = AwsUser.objects.get(
            user=self.request.user).aws_accounts.all()
        return Ec2SecurityGroup.objects.filter(aws_account__in=current_accounts)

    def get_context_data(self, **kwargs):
        context = super(Ec2SecurityGroupTableView, self).get_context_data(**kwargs)
        context['instance_id'] = self.request.GET.get('instance_id')
        context['loadbalancer_id'] = self.request.GET.get('loadbalancer_id')
        context['tag_id'] = self.request.GET.get('tag_id')
        return context


class Ec2SnapshotTableView(SingleTableView):
    model = Ec2Snapshot
    table_class = Ec2SnapshotTable

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Ec2SnapshotTableView, self).dispatch(*args, **kwargs)

    def get_table_data(self):
        AwsResourcesController(self.request.user).load_ec2_data()
        current_accounts = AwsUser.objects.get(
            user=self.request.user).aws_accounts.all()
        return Ec2Snapshot.objects.filter(aws_account__in=current_accounts)

    def get_context_data(self, **kwargs):
        context = super(Ec2SnapshotTableView, self).get_context_data(**kwargs)
        context['ami_id'] = self.request.GET.get('ami_id')
        context['instance_id'] = self.request.GET.get('instance_id')
        context['tag_id'] = self.request.GET.get('tag_id')
        context['volume_id_created'] = self.request.GET.get('volume_id_created')
        context['volume_id_creator'] = self.request.GET.get('volume_id_creator')
        return context


class Ec2TagTableView(SingleTableView):
    model = Ec2Tag
    table_class = Ec2TagTable

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Ec2TagTableView, self).dispatch(*args, **kwargs)

    def get_table_data(self):
        AwsResourcesController(self.request.user).load_ec2_data()
        current_accounts = AwsUser.objects.get(
            user=self.request.user).aws_accounts.all()
        return Ec2Tag.objects.filter(aws_account__in=current_accounts)

    def get_context_data(self, **kwargs):
        context = super(Ec2TagTableView, self).get_context_data(**kwargs)
        context['ami_id'] = self.request.GET.get('ami_id')
        context['instance_id'] = self.request.GET.get('instance_id')
        context['loadbalancer_id'] = self.request.GET.get('loadbalancer_id')
        context['securitygroup_id'] = self.request.GET.get('securitygroup_id')
        context['snapshot_id'] = self.request.GET.get('snapshot_id')
        context['volume_id'] = self.request.GET.get('volume_id')
        return context


class Ec2VolumeTableView(SingleTableView):
    model = Ec2Volume
    table_class = Ec2VolumeTable

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Ec2VolumeTableView, self).dispatch(*args, **kwargs)

    def get_table_data(self):
        AwsResourcesController(self.request.user).load_ec2_data()
        current_accounts = AwsUser.objects.get(
            user=self.request.user).aws_accounts.all()
        return Ec2Volume.objects.filter(aws_account__in=current_accounts)

    def get_context_data(self, **kwargs):
        context = super(Ec2VolumeTableView, self).get_context_data(**kwargs)
        context['instance_id'] = self.request.GET.get('instance_id')
        context['snapshot_id_created'] = self.request.GET.get('snapshot_id_created')
        context['snapshot_id_creator'] = self.request.GET.get('snapshot_id_creator')
        context['tag_id'] = self.request.GET.get('tag_id')
        return context
