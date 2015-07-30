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


import django_tables2 as tables
import arrow
from django.utils.html import format_html

from dashboard.vendor.tables_rendering import CustomColumnRendering
from dashboard.models.ec2.ec2_ami import Ec2Ami
from dashboard.models.ec2.ec2_elastic_ip import Ec2ElasticIp
from dashboard.models.ec2.ec2_keypair import Ec2Keypair
from dashboard.models.ec2.ec2_instance import Ec2Instance
from dashboard.models.ec2.ec2_load_balancer import Ec2LoadBalancer
from dashboard.models.ec2.ec2_security_group import Ec2SecurityGroup
from dashboard.models.ec2.ec2_snapshot import Ec2Snapshot
from dashboard.models.ec2.ec2_tag import Ec2Tag
from dashboard.models.ec2.ec2_volume import Ec2Volume

__author__ = 'Arnaud Desclouds <arnaud.software@use.startmail.com>'


class Ec2AmiTable(tables.Table):
    selected_ec2_amis = tables.CheckBoxColumn(accessor='pk')
    aws_account = tables.Column(accessor='aws_account.name',
                                verbose_name='aws account')
    region = tables.Column(accessor='region.region_name')

    instances = tables.Column(empty_values=(),
                              orderable=False,
                              verbose_name='instances created')
    tags = tables.Column(empty_values=())

    def render_selected_ec2_amis(self, record):
        context_dict = {
            self.context['instance_id']: record.ec2instance_set.all(),
            self.context['tag_id']: record.tags.all()}
        return CustomColumnRendering.render_selected_resources(record,
                                                               context_dict)

    def render_created_from_snapshot(self, record):
        return format_html('<a href=/ec2snapshots/?ami_id={}>{}</a>',
                           record.pk, record.created_from_snapshot.id)

    def render_instances(self, record):
        return CustomColumnRendering.render_attribute(record,
                                                      record.ec2instance_set,
                                                      'no instance')

    def render_tags(self, record):
        return CustomColumnRendering.render_tags(record)

    class Meta:
        model = Ec2Ami
        attrs = {'class': 'paleblue'}
        order_by = ('aws_account',
                    'region',
                    'ami_id')
        sequence = ('selected_ec2_amis',
                    'aws_account',
                    'region',
                    'ami_id')


class Ec2ElasticIpTable(tables.Table):
    selected_ec2_elastic_ips = tables.CheckBoxColumn(accessor='pk')
    aws_account = tables.Column(accessor='aws_account.name',
                                verbose_name='aws account')
    region = tables.Column(accessor='region.region_name')

    def render_instance_id(self, record):
        return CustomColumnRendering.render_attribute(record,
                                                      record.instance_id)

    def render_selected_ec2_elastic_ips(self, record):
        context_dict = {
            self.context['instance_id']: record.instance_id
        }
        return CustomColumnRendering.render_selected_resources(record,
                                                               context_dict)

    class Meta:
        model = Ec2ElasticIp
        attrs = {'class': 'paleblue'}
        order_by = ('aws_account',
                    'region',
                    'id')
        sequence = ('selected_ec2_elastic_ips',
                    'aws_account',
                    'region',
                    'public_ip',
                    'private_ip_address',
                    'instance_id')


class Ec2InstanceTable(tables.Table):
    selected_ec2_instances = tables.CheckBoxColumn(accessor='pk')
    architecture = tables.Column(visible=False)
    availability_zone = tables.Column(accessor='availability_zone.name',
                                      verbose_name='availability zone')
    aws_account = tables.Column(accessor='aws_account.name',
                                verbose_name='aws account')
    ec2_platform = tables.Column(verbose_name='platform')
    ec2_price = tables.Column(empty_values=(),
                              accessor='ec2_price.hourly_price',
                              verbose_name='hourly price')
    elastic_ip = tables.Column(empty_values=(),
                               orderable=False)
    kernel = tables.Column(visible=False)
    image_name = tables.Column(accessor='image_id.name',
                               verbose_name='image name')
    platform = tables.Column(visible=False)

    region_name = tables.Column(accessor='availability_zone.region.region_name')

    # attached set
    volumes = tables.Column(empty_values=(),
                            orderable=False)
    # m2m
    load_balancers = tables.Column(empty_values=(),
                                   orderable=False)
    security_groups = tables.Column(empty_values=())
    tags = tables.Column(empty_values=())

    def render_selected_ec2_instances(self, record):
        # OneToOne
        try:
            ip = record.ec2elasticip
        except Ec2ElasticIp.DoesNotExist:
            ip = None
        context_dict = {self.context['volume_id']: record.ec2volume_set.all(),
                        self.context[
                            'loadbalancer_id']: record.ec2loadbalancer_set.all(),
                        self.context[
                            'securitygroup_id']: record.security_groups.all(),
                        self.context['tag_id']: record.tags.all(),
                        self.context['ami_id']: record.image_id,
                        self.context['elasticip_id']: ip,
                        self.context['keypair_id']: record.key_name}
        return CustomColumnRendering.render_selected_resources(record,
                                                               context_dict)

    def render_ec2_price(self, column, record):
        if record.ec2_price:
            background_color = CustomColumnRendering.render_background_color(record)
            column.attrs = {'td': {'bgcolor': background_color}}
            return record.ec2_price.hourly_price
        else:
            column.attrs = {}
            return 'unknown'


    def render_elastic_ip(self, record):
        # OneToOne
        column = None
        try:
            column = CustomColumnRendering.render_attribute(record,
                                                            record.ec2elasticip)
        except Ec2ElasticIp.DoesNotExist:
            pass
        return column

    def render_key_name(self, record):
        return CustomColumnRendering.render_attribute(record,
                                                      record.key_name)

    def render_load_balancers(self, record):
        return CustomColumnRendering.render_attribute(record,
                                                      record.ec2loadbalancer_set)

    def render_security_groups(self, record):
        return CustomColumnRendering.render_attribute(record,
                                                      record.security_groups)

    def render_volumes(self, record):
        return CustomColumnRendering.render_attribute(record,
                                                      record.ec2volume_set,
                                                      'no volume attached')

    def render_tags(self, record):
        return CustomColumnRendering.render_tags(record)

    def render_image_id(self, record):
        return CustomColumnRendering.render_attribute(record,
                                                      record.image_id)

    def render_launch_time(self, value):
        return arrow.get(value).humanize()

    # Not possible because of issues:
    # - #211: https://github.com/bradleyayers/django-tables2/issues/211
    # - #229: https://github.com/bradleyayers/django-tables2/issues/229
    # ec2volume_set = tables.Column(accessor='ec2volume_set')

    class Meta:
        model = Ec2Instance
        # add class="paleblue" to <table> tag
        attrs = {'class': 'paleblue'}
        order_by = ('aws_account',
                    'region_name',
                    'availability_zone',
                    'instance_type',
                    'id')
        sequence = ('selected_ec2_instances',
                    'aws_account',
                    'region_name',
                    'availability_zone',
                    'instance_type',
                    'id',
                    '...',
                    'key_name',
                    'tags')


class Ec2KeypairTable(tables.Table):
    selected_ec2_keypairs = tables.CheckBoxColumn(accessor='pk')
    aws_account = tables.Column(accessor='aws_account.name',
                                verbose_name='aws_account')
    region = tables.Column(accessor='region.region_name')

    instances = tables.Column(empty_values=(),
                              orderable=False)

    def render_selected_ec2_keypairs(self, record):
        context_dict = {
            self.context['instance_id']: record.ec2instance_set.all()}
        return CustomColumnRendering.render_selected_resources(record,
                                                               context_dict)

    def render_instances(self, record):
        return CustomColumnRendering.render_attribute(record,
                                                      record.ec2instance_set,
                                                      'no instance')


    class Meta:
        model = Ec2Keypair
        attrs = {'class': 'paleblue'}
        order_by = ('aws_account',
                    'region',
                    'key_name')
        sequence = ('selected_ec2_keypairs',
                    'aws_account',
                    'region')


class Ec2LoadBalancerTable(tables.Table):
    selected_ec2_load_balancers = tables.CheckBoxColumn(accessor='pk')
    aws_account = tables.Column(accessor='aws_account.name',
                                verbose_name='aws account')
    instances = tables.Column(empty_values=())
    region = tables.Column(accessor='region.region_name')
    security_groups = tables.Column(empty_values=())

    def render_selected_ec2_load_balancers(self, record):
        context_dict = {
            self.context['instance_id']: record.instances.all(),
            self.context['securitygroup_id']: record.security_groups.all()

        }
        return CustomColumnRendering.render_selected_resources(record,
                                                               context_dict)

    def render_security_groups(self, record):
        return CustomColumnRendering.render_attribute(record,
                                                      record.security_groups)

    def render_created_time(self, value):
        return arrow.get(value).humanize()

    def render_instances(self, record):
        return CustomColumnRendering.render_attribute(record,
                                                      record.instances)

    class Meta:
        model = Ec2LoadBalancer
        attrs = {'class': 'paleblue'}
        order_by = ('aws_account',
                    'region',
                    'name',
                    'id')
        sequence = ('selected_ec2_load_balancers',
                    'aws_account',
                    'region',
                    'id',
                    'name')


class Ec2SecurityGroupTable(tables.Table):
    selected_ec2_security_groups = tables.CheckBoxColumn(accessor='pk')
    aws_account = tables.Column(accessor='aws_account.name',
                                verbose_name='aws account')
    instances = tables.Column(empty_values=(),
                              orderable=False)
    load_balancers = tables.Column(empty_values=(),
                                   orderable=False)
    region = tables.Column(accessor='region.region_name')
    tags = tables.Column(empty_values=())

    def render_selected_ec2_security_groups(self, record):
        context_dict = {
            self.context['instance_id']: record.ec2instance_set.all(),
            self.context['loadbalancer_id']: record.ec2loadbalancer_set.all(),
            self.context['tag_id']: record.tags.all()
        }
        return CustomColumnRendering.render_selected_resources(record,
                                                               context_dict)

    def render_instances(self, record):
        return CustomColumnRendering.render_attribute(record,
                                                      record.ec2instance_set,
                                                      empty='')

    def render_load_balancers(self, record):
        return CustomColumnRendering.render_attribute(record,
                                                      record.ec2loadbalancer_set,
                                                      empty='')

    def render_tags(self, record):
        return CustomColumnRendering.render_tags(record)

    class Meta:
        model = Ec2SecurityGroup
        attrs = {'class': 'paleblue'}
        order_by = ('aws_account',
                    'region',
                    'name',
                    'id')
        sequence = ('selected_ec2_security_groups',
                    'aws_account',
                    'region',
                    'id',
                    'name',
                    'description',
                    'owner_id')


class Ec2SnapshotTable(tables.Table):
    selected_ec2_snapshots = tables.CheckBoxColumn(accessor='pk')
    aws_account = tables.Column(accessor='aws_account.name',
                                verbose_name='aws account')
    region = tables.Column(accessor='region.region_name')

    created_volumes = tables.Column(empty_values=(),
                                    orderable=False)
    tags = tables.Column(empty_values=())

    def render_created_from_volume(self, record):
        return format_html('<a href=/ec2volumes/?snapshot_id_created={}>{}</a>',
                           record.id, record.created_from_volume.id)

    def render_created_volumes(self, record):
        return CustomColumnRendering.render_attribute(record,
                                                      record.ec2volume_set,
                                                      empty='',
                                                      custom_param_name='snapshot_id_creator')

    def render_selected_ec2_snapshots(self, record):
        context_dict = {
            self.context['volume_id_created']: record.ec2volume_set.all(),
            self.context['volume_id_creator']: record.created_from_volume,
            self.context['ami_id']: record.ec2ami_set.all(),
            self.context['tag_id']: record.tags.all()}
        return CustomColumnRendering.render_selected_resources(record,
                                                               context_dict)

    def render_start_time(self, value):
        return arrow.get(value).humanize()

    def render_tags(self, record):
        return CustomColumnRendering.render_tags(record)

    class Meta:
        model = Ec2Snapshot
        attrs = {'class': 'paleblue'}
        order_by = ('aws_account',
                    'region',
                    'id')
        sequence = ('selected_ec2_snapshots',
                    'aws_account',
                    'region',
                    'id',
                    'start_time')


class Ec2TagTable(tables.Table):
    selected_ec2_tags = tables.CheckBoxColumn(accessor='pk')
    id = tables.Column(visible=False)
    aws_account = tables.Column(accessor='aws_account.name',
                                verbose_name='aws account')
    region = tables.Column(accessor='region.region_name')

    amis = tables.Column(empty_values=(),
                         orderable=False,
                         verbose_name='AMIs')
    instances = tables.Column(empty_values=(),
                              orderable=False,
                              verbose_name='Instances')
    security_groups = tables.Column(empty_values=(),
                                    orderable=False,
                                    verbose_name='Security Groups')
    snapshots = tables.Column(empty_values=(),
                              orderable=False,
                              verbose_name='Snapshots')
    volumes = tables.Column(empty_values=(),
                            orderable=False,
                            verbose_name='Volumes')

    def render_selected_ec2_tags(self, record):
        context_dict = {
            self.context['ami_id']: record.ec2ami_set.all(),
            self.context['instance_id']: record.ec2instance_set.all(),
            self.context['loadbalancer_id']: record.ec2loadbalancer_set.all(),
            self.context['securitygroup_id']: record.ec2securitygroup_set.all(),
            self.context['snapshot_id']: record.ec2snapshot_set.all(),
            self.context['volume_id']: record.ec2volume_set.all(),
        }
        return CustomColumnRendering.render_selected_resources(record,
                                                               context_dict)

    def render_amis(self, record):
        return CustomColumnRendering.render_attribute(record,
                                                      record.ec2ami_set,
                                                      empty='')

    def render_instances(self, record):
        return CustomColumnRendering.render_attribute(record,
                                                      record.ec2instance_set,
                                                      empty='')

    def render_security_groups(self, record):
        return CustomColumnRendering.render_attribute(record,
                                                      record.ec2securitygroup_set,
                                                      empty='')

    def render_snapshots(self, record):
        return CustomColumnRendering.render_attribute(record,
                                                      record.ec2snapshot_set,
                                                      empty='')

    def render_volumes(self, record):
        return CustomColumnRendering.render_attribute(record,
                                                      record.ec2volume_set,
                                                      empty='')

    class Meta:
        model = Ec2Tag
        attrs = {'class': 'paleblue'}
        order_by = ('aws_account',
                    'region',
                    'key',
                    'value')
        sequence = ('selected_ec2_tags',
                    'aws_account',
                    'region',
                    'key',
                    'value')


class Ec2VolumeTable(tables.Table):
    selected_ec2_volumes = tables.CheckBoxColumn(accessor='pk')

    availability_zone = tables.Column(accessor='availability_zone.name',
                                      verbose_name='availability zone')
    aws_account = tables.Column(accessor='aws_account.name',
                                verbose_name='aws account')

    instance_id = tables.Column(verbose_name='attached to instance')

    region_name = tables.Column(accessor='availability_zone.region.region_name')

    created_snapshots = tables.Column(empty_values=(),
                                      orderable=False,
                                      verbose_name='created snapshots')

    tags = tables.Column(empty_values=())

    def render_created_from_snapshot(self, record):
        return format_html('<a href=/ec2snapshots/?volume_id_created={}>{}</a>',
                           record.id, record.created_from_snapshot.id)

    def render_created_snapshots(self, record):
        return CustomColumnRendering.render_attribute(record,
                                                      record.ec2snapshot_set,
                                                      empty='',
                                                      custom_param_name='volume_id_creator')

    def render_selected_ec2_volumes(self, record):
        context_dict = {
            self.context['snapshot_id_created']: record.ec2snapshot_set.all(),
            self.context['snapshot_id_creator']: record.created_from_snapshot,
            self.context['instance_id']: record.instance_id,
            self.context['tag_id']: record.tags.all()}
        return CustomColumnRendering.render_selected_resources(record,
                                                               context_dict)

    def render_instance_id(self, record):
        if record.instance_id:
            return format_html('<a href=/ec2instances/?volume_id={}>{}</a>',
                               record.id, record.instance_id.id)
        else:
            return 'no volume attached'

    def render_attach_time(self, value):
        return arrow.get(value).humanize() if value else 'detached'

    def render_create_time(self, value):
        return arrow.get(value).humanize()

    def render_tags(self, record):
        return CustomColumnRendering.render_tags(record)

    class Meta:
        model = Ec2Volume
        attrs = {'class': 'paleblue'}
        order_by = ('aws_account',
                    'region_name',
                    'availability_zone',
                    'id')
        sequence = ('selected_ec2_volumes',
                    'aws_account',
                    'region_name',
                    'availability_zone',
                    'id',
                    'create_time',
                    'attach_time',
                    'instance_id',
                    '...',
                    'type',
                    'tags')
