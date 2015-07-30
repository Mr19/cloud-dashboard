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

from cloud_dashboard.common.utils.scrape import scrape
from aws_account.models import AwsUser
from dashboard.models.ec2.ec2_instance import Ec2Instance
from dashboard.models.prices.ec2_price import Ec2Price
from dashboard.models.regions.region import Region

__author__ = 'Arnaud Desclouds <arnaud.software@use.startmail.com>'


def scrape_prices(user):
    forbidden_region_names = ['cn-north-1', 'us-gov-west-1']
    aws_user = AwsUser.objects.get(user=user)
    instances_list = scrape()
    for instance in instances_list:
        for region in instance.pricing:
            if region not in forbidden_region_names:
                for ec2_platform in instance.pricing[region]:
                    try:
                        Ec2Price.objects.update_or_create(
                            instance_type=instance.instance_type,
                            ec2_platform=ec2_platform,
                            region=Region.objects.get(region_name=region),
                            defaults={
                                'hourly_price': instance.pricing[region][
                                    ec2_platform]
                            })
                    except Exception as e:
                        print(e)
                        continue
    aws_user.prices_last_updated = datetime.now(timezone.utc)
    aws_user.save()


def add_instance_prices():
    for ec2_instance in Ec2Instance.objects.all():
        try:
            ec2_instance.ec2_price = Ec2Price.objects.get(
                ec2_platform=ec2_instance.ec2_platform,
                instance_type=ec2_instance.instance_type,
                region=ec2_instance.availability_zone.region)
        except Ec2Price.DoesNotExist:
            continue
        ec2_instance.save()
