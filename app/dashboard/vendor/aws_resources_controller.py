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


from datetime import datetime
from datetime import timezone

import boto.ec2
import boto.ec2.elb
import django_rq

from dashboard.models.regions.availability_zone import AvailabilityZone
from dashboard.models.regions.region import Region
from aws_account.models import AwsUser
from dashboard.vendor.aws_prices import add_instance_prices
from dashboard.vendor.aws_prices import scrape_prices
from dashboard.vendor.aws_resources_reception import receive_amis_async
from dashboard.vendor.aws_resources_reception import receive_elastic_ips_async
from dashboard.vendor.aws_resources_reception import receive_instances_async
from dashboard.vendor.aws_resources_reception import receive_keypairs_async
from dashboard.vendor.aws_resources_reception import receive_load_balancers_async
from dashboard.vendor.aws_resources_reception import receive_security_groups_async
from dashboard.vendor.aws_resources_reception import receive_snapshots_async
from dashboard.vendor.aws_resources_reception import receive_volumes_async
from dashboard.vendor.exceptions import NoAwsAccountException

__author__ = 'Arnaud Desclouds <arnaud.software@use.startmail.com>'



class AwsResourcesController(object):
    __FORBIDDEN_REGIONS_NAMES = ['cn-north-1', 'us-gov-west-1']
    __CONNECTIONS = {}
    __ELB_CONNECTIONS = {}

    def __init__(self, user):
        self.user = user

    def initialize_connections(self):
        for region in Region.objects.all():
            aws_user = AwsUser.objects.get(user=self.user)
            aws_accounts = aws_user.aws_accounts.all()

            if not aws_accounts:
                raise NoAwsAccountException('No AWS Account found!')

            for aws_account in aws_accounts:
                self.__CONNECTIONS[(aws_account.name,
                                    region.region_name)] = boto.ec2.connect_to_region(
                    region.region_name,
                    aws_access_key_id=aws_account.aws_access_key_id,
                    aws_secret_access_key=aws_account.aws_secret_access_key)

                self.__ELB_CONNECTIONS[(aws_account.name,
                                        region.region_name)] = boto.ec2.elb.connect_to_region(
                    region.region_name,
                    aws_access_key_id=aws_account.aws_access_key_id,
                    aws_secret_access_key=aws_account.aws_secret_access_key)

    def change_state_ec2_instances(self, ec2_instances, new_state):
        self.initialize_connections()
        ec2_instances_changed = []
        for ec2_instance in ec2_instances:
            if new_state == 'stopped':
                ec2_instances_changed.extend(self.__CONNECTIONS[
                                                 (ec2_instance.aws_account.name,
                                                  ec2_instance.availability_zone.region.region_name)
                                             ].stop_instances(ec2_instance.id))
            elif new_state == 'terminated':
                ec2_instances_changed.extend(self.__CONNECTIONS[
                                                 (ec2_instance.aws_account.name,
                                                  ec2_instance.availability_zone.region.region_name)
                                             ].terminate_instances(
                    ec2_instance.id))
        return ec2_instances_changed

    def change_state_ec2_volumes(self, ec2_volumes, new_state):
        self.initialize_connections()
        ec2_volumes_changed = []
        for ec2_volume in ec2_volumes:
            try:
                if new_state == 'detached':
                    if self.__CONNECTIONS[
                        (ec2_volume.aws_account.name,
                         ec2_volume.availability_zone.region.region_name)
                    ].detach_volume(ec2_volume.id,
                                    instance_id=ec2_volume.instance_id.id):
                        ec2_volumes_changed.append(ec2_volume.id)
                elif new_state == 'deleted':
                    if self.__CONNECTIONS[
                        (ec2_volume.aws_account.name,
                         ec2_volume.availability_zone.region.region_name)
                    ].delete_volume(ec2_volume.id):
                        ec2_volumes_changed.append(ec2_volume.id)
            except Exception as e:
                print(e)
                continue
        return ec2_volumes_changed

    def load_ec2_data(self):
        if not Region.objects.all():
            self._initialize_regions_and_availability_zones()
        user = AwsUser.objects.get(user=self.user)

        update_resources = False
        update_prices = False
        if not user.resources_up_to_date():
            self.update_resources_timestamp()
            update_resources = True

        if not user.prices_up_to_date():
            self.update_prices_timestamp()
            update_prices = True

        if update_resources:
            self.receive_resources_async()
            scrape_prices(self.user.id)
        if update_prices:
            queue = django_rq.get_queue('high')
            queue.enqueue(scrape_prices, self.user.id)


    def manually_update_ec2_data(self):
        if not Region.objects.all():
            self._initialize_regions_and_availability_zones()
        self.receive_resources_async()

    def manually_update_prices(self):
        queue = django_rq.get_queue('high')
        queue.enqueue(scrape_prices, self.user.id)
        queue.enqueue(add_instance_prices)

    def _initialize_regions_and_availability_zones(self):
        for region in boto.ec2.regions():
            if region.name not in self.__FORBIDDEN_REGIONS_NAMES:
                aws_user = AwsUser.objects.get(user=self.user)
                aws_account = aws_user.aws_accounts.first()

                if not aws_account:
                    raise NoAwsAccountException('No AWS Account found!')

                self.__CONNECTIONS[region.name] = boto.ec2.connect_to_region(
                    region.name,
                    aws_access_key_id=aws_account.aws_access_key_id,
                    aws_secret_access_key=aws_account.aws_secret_access_key)
                new_region = Region.objects.create(region_name=region.name)

                availability_zones = self.__CONNECTIONS[
                    region.name].get_all_zones()

                for zone in availability_zones:
                    AvailabilityZone.objects.create(name=zone.name,
                                                    region=new_region)


    def update_resources_timestamp(self):
        aws_user = AwsUser.objects.get(user=self.user)
        aws_user.resources_last_updated = datetime.now(timezone.utc)
        aws_user.save()

    def update_prices_timestamp(self):
        aws_user = AwsUser.objects.get(user=self.user)
        aws_user.prices_last_updated = datetime.now(timezone.utc)
        aws_user.save()

    def receive_resources_async(self):
        aws_user = AwsUser.objects.get(user=self.user)
        aws_user.resources_last_updated = datetime.now(timezone.utc)
        aws_user.save()


        self.initialize_connections()
        aws_accounts = aws_user.aws_accounts.all()
        regions = Region.objects.all()
        params = {'connections': self.__CONNECTIONS,
                  'regions': regions,
                  'aws_accounts': aws_accounts}

        queue = django_rq.get_queue('high')

        queue.enqueue(receive_keypairs_async, **params)
        queue.enqueue(receive_security_groups_async, **params)
        queue.enqueue(receive_amis_async, **params)
        queue.enqueue(receive_instances_async, **params)
        queue.enqueue(add_instance_prices)
        queue.enqueue(receive_snapshots_async, **params)
        queue.enqueue(receive_volumes_async, **params)
        queue.enqueue(receive_elastic_ips_async, **params)
        queue.enqueue(receive_load_balancers_async,
                      self.__ELB_CONNECTIONS,
                      regions,
                      aws_accounts)
