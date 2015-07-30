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


from django.db import IntegrityError
from boto.exception import EC2ResponseError

from dashboard.vendor.introspection import introspect
from dashboard.models.ec2.ec2_ami import Ec2Ami
from dashboard.models.ec2.ec2_elastic_ip import Ec2ElasticIp
from dashboard.models.ec2.ec2_instance import Ec2Instance
from dashboard.models.ec2.ec2_keypair import Ec2Keypair
from dashboard.models.ec2.ec2_load_balancer import Ec2LoadBalancer
from dashboard.models.ec2.ec2_security_group import Ec2SecurityGroup
from dashboard.models.ec2.ec2_snapshot import Ec2Snapshot
from dashboard.models.ec2.ec2_tag import Ec2Tag
from dashboard.models.ec2.ec2_volume import Ec2Volume
from dashboard.models.regions.availability_zone import AvailabilityZone
from dashboard.models.regions.region import Region

__author__ = 'Arnaud Desclouds <arnaud.software@use.startmail.com>'


def receive_keypairs_async(connections, regions, aws_accounts):
    """Retrieves keypairs from AWS, is used as a job for RQ (Redis Queue).

    Connects to AWS in the given regions with the given aws_accounts credentials
    and retrieves the keypairs. Persist those keypairs in the database.

    Args:
        connections: The connections dictionary containing the connections to
            AWS.
        regions: The Django Regions objects on which to retrieve keypairs.
        aws_accounts: The Django AwsAccounts objects on which to retrieve
        keypairs.
    """
    print('BEGIN RECEIVE KEYPAIRS ASYNC')
    for region in regions:
        for aws_account in aws_accounts:
            # Keypairs
            boto_keypairs = connections[
                (aws_account.name, region.region_name)].get_all_key_pairs()
            for boto_keypair in boto_keypairs:
                ec2_keypair_defaults = introspect(boto_keypair, Ec2Keypair)
                ec2_keypair_defaults['aws_account'] = aws_account
                ec2_keypair_defaults['region'] = Region.objects.get(
                    region_name=boto_keypair.region.name)
                Ec2Keypair.objects.update_or_create(key_name=boto_keypair.name,
                                                    defaults=ec2_keypair_defaults)
    print('END RECEIVE KEYPAIRS ASYNC')


def receive_security_groups_async(connections, regions, aws_accounts):
    """Retrieves security groups from AWS, is used as a job for RQ (Redis Queue).

    Args:
        connections: The connections dictionary containing the connections to
            AWS.
        regions: The Django Regions objects on which to retrieve security
        groups.
        aws_accounts: The Django AwsAccounts objects on which to retrieve
        security groups.
    """
    print('BEGIN RECEIVE SECURITY GROUPS ASYNC')
    for region in regions:
        for aws_account in aws_accounts:
            # Security Groups
            boto_security_groups = connections[(
                aws_account.name, region.region_name)].get_all_security_groups()
            for boto_security_group in boto_security_groups:
                ec2_security_group_defaults = introspect(
                    boto_security_group, Ec2SecurityGroup)
                ec2_security_group_defaults['aws_account'] = aws_account
                ec2_security_group_defaults['region'] = Region.objects.get(
                    region_name=boto_security_group.region.name)
                (security_group,
                 created) = Ec2SecurityGroup.objects.update_or_create(
                    id=boto_security_group.id,
                    defaults=ec2_security_group_defaults)

                # Security group tags
                _add_resource_tags(boto_security_group, security_group)
    print('END RECEIVE SECURITY GROUPS ASYNC')


def receive_amis_async(connections, regions, aws_accounts):
    """Retrieves AMIs from AWS, is used as a job for RQ (Redis Queue).

    Connects to AWS in the given regions with the given aws_accounts credentials
    and retrieves the AMIs. Persist those AMIs in the database.

    Args:
        connections: The connections dictionary containing the connections to
            AWS.
        regions: The Django Regions objects on which to retrieve AMIs.
        aws_accounts: The Django AwsAccounts objects on which to retrieve
        AMIs.
    """
    print('BEGIN RECEIVE AMIS ASYNC')
    for region in regions:
        for aws_account in aws_accounts:
            reservations = connections[(
                aws_account.name, region.region_name)].get_all_reservations()
            for reservation in reservations:
                for instance in reservation.instances:
                    availability_zone = AvailabilityZone.objects.get(
                        name=instance.placement)

                    # AMIs
                    boto_ami = connections[(aws_account.name, region.region_name)].get_image(image_id=instance.image_id)
                    ec2_ami_defaults = introspect(boto_ami, Ec2Ami)
                    ec2_ami_defaults['aws_account'] = aws_account
                    # Sometimes AWS gives us a NoneType
                    if boto_ami:
                        ec2_ami_defaults['region'] = Region.objects.get(region_name=boto_ami.region.name)
                        if boto_ami.block_device_mapping.current_value.snapshot_id:
                            try:
                                ec2_snapshot_defaults = introspect(connections[(aws_account.name,region.region_name)].get_all_snapshots(snapshot_ids=[boto_ami.block_device_mapping.current_value.snapshot_id]),Ec2Snapshot)
                                ec2_snapshot_defaults['region'] = region
                                ec2_ami_defaults['created_from_snapshot'] = \
                                    Ec2Snapshot.objects.get_or_create(
                                        id=boto_ami.block_device_mapping.current_value.snapshot_id,
                                        defaults=ec2_snapshot_defaults)[0]
                            except EC2ResponseError as e:
                                print(e)

                    (ami, ami_created) = Ec2Ami.objects.update_or_create(
                        ami_id=instance.image_id,
                        defaults=ec2_ami_defaults)

                    if boto_ami:
                        _add_resource_tags(boto_ami, ami)


            boto_amis = connections[(
                aws_account.name, region.region_name)].get_all_images(owners=['self'])
            for boto_ami in boto_amis:
                if boto_ami:
                    ec2_ami_defaults = introspect(boto_ami, Ec2Ami)
                    ec2_ami_defaults['aws_account'] = aws_account
                    if boto_ami.block_device_mapping.current_value.snapshot_id:
                        try:
                            ec2_snapshot_defaults = introspect(connections[(aws_account.name, region.region_name)].get_all_snapshots(snapshot_ids=[boto_ami.block_device_mapping.current_value.snapshot_id]), Ec2Snapshot)
                            ec2_snapshot_defaults['region'] = region
                            ec2_ami_defaults['created_from_snapshot'] = Ec2Snapshot.objects.get_or_create(
                                    id=boto_ami.block_device_mapping.current_value.snapshot_id,
                                    defaults=ec2_snapshot_defaults)[0]
                        except (EC2ResponseError, IntegrityError) as e:
                            print(e)
                    try:
                        (obj, created) = Ec2Ami.objects.update_or_create(
                            ami_id=boto_ami.id,
                            defaults=ec2_ami_defaults)
                        # AMI tags
                        _add_resource_tags(boto_ami, obj)
                    except IntegrityError as e:
                        print(e)

    print('END RECEIVE AMIS ASYNC')


def receive_instances_async(connections, regions, aws_accounts):
    """Retrieves instances from AWS, is used as a job for RQ (Redis Queue).

    Connects to AWS in the given regions with the given aws_accounts credentials
    and retrieves the instances. Persist those instances in the database.

    Args:
        connections: The connections dictionary containing the connections to
            AWS.
        regions: The Django Regions objects on which to retrieve instances.
        aws_accounts: The Django AwsAccounts objects on which to retrieve
        instances.
    """
    print('BEGIN RECEIVE INSTANCES ASYNC')
    instances_created = False
    for region in regions:
        for aws_account in aws_accounts:
            reservations = connections[(
                aws_account.name, region.region_name)].get_all_reservations()
            for reservation in reservations:
                for instance in reservation.instances:
                    availability_zone = AvailabilityZone.objects.get(
                        name=instance.placement)
                    for v in instance.block_device_mapping.values():
                        ec2_volume_defaults = introspect(v, Ec2Volume)
                        ec2_volume_defaults['aws_account'] = aws_account
                        Ec2Volume.objects.update_or_create(id=v.volume_id,
                                                           defaults=ec2_volume_defaults)

                    ec2_instance_defaults = introspect(instance,
                                                       Ec2Instance)
                    ec2_instance_defaults['aws_account'] = aws_account
                    ec2_instance_defaults['availability_zone'] = availability_zone

                    try:
                        ami = Ec2Ami.objects.get(pk=instance.image_id)
                        ec2_instance_defaults['image_id'] = ami
                        ec2_instance_defaults['ec2_platform'] = _get_ec2_platform(instance.platform, ami.name)
                    except Ec2Ami.DoesNotExist as e:
                        print(e)


                    try:
                        key_name = Ec2Keypair.objects.get(
                            key_name=instance.key_name)
                        ec2_instance_defaults['key_name'] = key_name
                    except Ec2Keypair.DoesNotExist as e:
                        print(e)

                    try:
                        (obj, created) = Ec2Instance.objects.update_or_create(
                                id=instance.id,
                                defaults=ec2_instance_defaults)
                        if created:
                            instances_created = True
                    except IntegrityError as e:
                        print(e)


                    # Instance security groups
                    for sg in instance.groups:
                        try:
                            (ec2_security_group, created) = Ec2SecurityGroup.objects.update_or_create(
                                id=sg.id,
                                defaults=introspect(sg, Ec2SecurityGroup))
                            obj.security_groups.add(ec2_security_group)
                        except IntegrityError as e:
                            print(e)

                    # Instance tags
                    _add_resource_tags(instance, obj)

    print('END RECEIVE INSTANCES ASYNC')
    return instances_created


def receive_snapshots_async(connections, regions, aws_accounts):
    """Retrieves snapshots from AWS, is used as a job for RQ (Redis Queue).

    Connects to AWS in the given regions with the given aws_accounts credentials
    and retrieves the snapshots. Persist those snapshots in the database.

    Args:
        connections: The connections dictionary containing the connections to
            AWS.
        regions: The Django Regions objects on which to retrieve snapshots.
        aws_accounts: The Django AwsAccounts objects on which to retrieve
        snapshots.
    """
    print('BEGIN RECEIVE SNAPSHOTS ASYNC')
    for region in regions:
        for aws_account in aws_accounts:
            # Snapshots
            boto_snapshots = connections[
                (aws_account.name, region.region_name)].get_all_snapshots(
                owner=['self'])
            for boto_snapshot in boto_snapshots:
                ec2_snapshot_defaults = introspect(boto_snapshot,
                                                   Ec2Snapshot)
                ec2_snapshot_defaults['aws_account'] = aws_account
                ec2_snapshot_defaults['region'] = Region.objects.get(
                    region_name=boto_snapshot.region.name)
                if boto_snapshot.volume_id:
                    try:
                        created_from_volume = \
                        Ec2Volume.objects.get_or_create(
                            id=boto_snapshot.volume_id,
                            defaults=introspect(connections[(
                            aws_account.name,
                            region.region_name)].get_all_volumes(
                                volume_ids=[boto_snapshot.volume_id]),
                                                Ec2Volume))[0]
                        ec2_snapshot_defaults[
                            'created_from_volume'] = created_from_volume
                    except EC2ResponseError:
                        print('Boto volume not found: ' + boto_snapshot.volume_id)

                (snapshot, created) = Ec2Snapshot.objects.update_or_create(
                    id=boto_snapshot.id,
                    defaults=ec2_snapshot_defaults)

                # Snapshot tags
                _add_resource_tags(boto_snapshot, snapshot)
    print('END RECEIVE SNAPSHOTS ASYNC')


def receive_volumes_async(connections, regions, aws_accounts):
    """Retrieves volumes from AWS, is used as a job for RQ (Redis Queue).

    Connects to AWS in the given regions with the given aws_accounts credentials
    and retrieves the volumes. Persist those volumes in the database.

    Args:
        connections: The connections dictionary containing the connections to
            AWS.
        regions: The Django Regions objects on which to retrieve volumes.
        aws_accounts: The Django AwsAccounts objects on which to retrieve
        volumes.
    """
    print('BEGIN RECEIVE VOLUMES ASYNC')
    for region in regions:
        for aws_account in aws_accounts:
            # Volumes
            boto_volumes = connections[
                (aws_account.name, region.region_name)].get_all_volumes()
            for boto_volume in boto_volumes:
                ec2_volume_defaults = introspect(boto_volume, Ec2Volume)
                ec2_volume_defaults['aws_account'] = aws_account
                ec2_volume_defaults['availability_zone'
                ] = AvailabilityZone.objects.get(name=boto_volume.zone)

                ec2_volume_defaults[
                    'attach_time'] = boto_volume.attach_data.attach_time
                try:
                    ec2_volume_defaults[
                        'instance_id'] = Ec2Instance.objects.get(
                        pk=boto_volume.attach_data.instance_id)
                except Ec2Instance.DoesNotExist:
                    ec2_volume_defaults['instance_id'] = None
                if boto_volume.snapshot_id:
                    print(boto_volume.snapshot_id)
                    try:
                        snapshot = connections[(aws_account.name, region.region_name)].get_all_snapshots(snapshot_ids=[boto_volume.snapshot_id])
                    except EC2ResponseError as e:
                        print(e)

                    try:
                        ec2_snapshot_defaults = introspect(snapshot, Ec2Snapshot)
                        ec2_snapshot_defaults['region'] = region
                        created_from_snapshot = Ec2Snapshot.objects.get_or_create(
                            id=boto_volume.snapshot_id,
                            defaults=ec2_snapshot_defaults)[0]
                        ec2_volume_defaults[
                            'created_from_snapshot'] = created_from_snapshot
                    except Exception as e:
                        print(e)

                try:
                    (volume, created) = Ec2Volume.objects.update_or_create(
                        id=boto_volume.id,
                        defaults=ec2_volume_defaults)
                    # Volume tags
                    _add_resource_tags(boto_volume, volume)
                except IntegrityError as e:
                    print(e)
    print('END RECEIVE VOLUMES ASYNC')


def receive_elastic_ips_async(connections, regions, aws_accounts):
    """Retrieves elastic IPs from AWS, is used as a job for RQ (Redis Queue).

    Connects to AWS in the given regions with the given aws_accounts credentials
    and retrieves the elastic IPs. Persist those elastic IPs in the database.

    Args:
        connections: The connections dictionary containing the connections to
            AWS.
        regions: The Django Regions objects on which to retrieve elastic IPs.
        aws_accounts: The Django AwsAccounts objects on which to retrieve
        elastic IPs.
    """
    print('BEGIN RECEIVE ELASTIC IPS ASYNC')
    for region in regions:
        for aws_account in aws_accounts:
            # Elastic IPs
            boto_elastic_ips = connections[
                (aws_account.name, region.region_name)].get_all_addresses()
            for boto_elastic_ip in boto_elastic_ips:
                ec2_elastic_ip_defaults = introspect(boto_elastic_ip,
                                                     Ec2ElasticIp)
                ec2_elastic_ip_defaults['aws_account'] = aws_account
                ec2_elastic_ip_defaults['region'] = Region.objects.get(
                    region_name=boto_elastic_ip.region.name)
                if boto_elastic_ip.instance_id:
                    ec2_elastic_ip_defaults[
                        'instance_id'] = Ec2Instance.objects.get(
                        pk=boto_elastic_ip.instance_id)
                Ec2ElasticIp.objects.update_or_create(
                    public_ip=boto_elastic_ip.public_ip,
                    defaults=ec2_elastic_ip_defaults)
    print('END RECEIVE ELASTIC IPS ASYNC')


def receive_load_balancers_async(elb_connections, regions, aws_accounts):
    """Retrieves load balancers from AWS, is used as a job for RQ (Redis Queue).

    Connects to AWS in the given regions with the given aws_accounts credentials
    and retrieves the load balancers. Persist those load balancers in the database.

    Args:
        connections: The connections dictionary containing the connections to
            AWS.
        regions: The Django Regions objects on which to retrieve load balancers.
        aws_accounts: The Django AwsAccounts objects on which to retrieve
        load balancers.
    """
    print('BEGIN RECEIVE LOAD BALANCERS ASYNC')
    for region in regions:
        for aws_account in aws_accounts:
             # Load Balancers
            boto_load_balancers = elb_connections[(
            aws_account.name, region.region_name)].get_all_load_balancers()
            for boto_load_balancer in boto_load_balancers:
                ec2_load_balancer_defaults = introspect(boto_load_balancer,
                                                        Ec2LoadBalancer)
                ec2_load_balancer_defaults['aws_account'] = aws_account
                (lb, created) = Ec2LoadBalancer.objects.update_or_create(
                    name=boto_load_balancer.name,
                    region=Region.objects.get(
                        region_name=region.region_name),
                    defaults=ec2_load_balancer_defaults)
                # Load Balancer tags
                # Not possible because of bug #2549 :
                # https://github.com/boto/boto/issues/2549

                # Impossible because source_security_group does not have
                # an id.
                # lb.security_groups.add(Ec2SecurityGroup.objects.get(name=boto_load_balancer.source_security_group.id))

                # Load Balancer - Security Groups
                for sg in boto_load_balancer.security_groups:
                    ec2_security_group = Ec2SecurityGroup.objects.get(
                        id=sg)
                    lb.security_groups.add(ec2_security_group)

                # Load Balancer - Instances
                for i in boto_load_balancer.instances:
                    ec2_instance = Ec2Instance.objects.get(id=i.id)
                    lb.instances.add(ec2_instance)

                # Load Balancer - Availability Zones
                for az in boto_load_balancer.availability_zones:
                    availability_zone = AvailabilityZone.objects.get(
                        name=az)
                    lb.availability_zones.add(availability_zone)
    print('END RECEIVE LOAD BALANCERS ASYNC')


def _add_resource_tags(boto_resource, resource, region=None):
    """Create and add Ec2Tag objects to a resource.

    Create Ec2Tag objects that are linked the boto_resource, and add them
    to the resource.

    Args:
        boto_resource: The boto resource possessing the tags.
        resource: The Django resource to add tags to.
        region: The region to which the resource belongs.
    """
    for k, v in boto_resource.tags.items():
        resource_region = None
        try:
            resource_region = resource.region
        except AttributeError:
            pass
        if not resource_region:
            try:
                resource_region = resource.availability_zone.region
            except AttributeError:
                # no region
                continue
        (ec2_tag, ec2_tag_created) = Ec2Tag.objects.get_or_create(key=k,
                                                                  value=v,
                                                                  aws_account=resource.aws_account,
                                                                  region=resource_region)
        resource.tags.add(ec2_tag)


def _get_ec2_platform(instance_platform, ami_name):
    """Returns the platform of an instance.

    For an instance's platform boto returns either the string 'windows' or None.
    It is necessary to determine the price of an instance to know which type
    of Windows the resources uses, currently there is four different types on
    the EC2 price page: https://aws.amazon.com/ec2/pricing/, 'Windows',
    'Windows with SQL Standard', 'Windows with SQL Web' and
    'Windows with SQL Enterprise'. That function determines the type of the
    instance between those four windows and linux and returns it.

    Args:
        instance_platform: The instance from which to determine its platform.
        ami_name: The name of the AMI of the instance.

    Returns:
        A string being either 'linux', 'Windows', 'Windows with SQL Standard',
        'Windows with SQL Web', 'Windows with SQL Enterprise' or
        'windows-unknown' in case the Windows type of the instance is unknown.
    """
    ami_name = ami_name.lower()
    if not instance_platform:
        return 'linux'
    elif instance_platform == 'windows':
        if 'sql' and 'web' in ami_name:
            return 'mswinSQLWeb'
        elif 'sql' and 'enterprise' in ami_name:
            return 'mswinSQLEnterprise'
        elif 'sql' in ami_name:
            return 'mswinSQL'
        elif ami_name:
            return 'mswin'
        else:
            return 'windows-unknown'
