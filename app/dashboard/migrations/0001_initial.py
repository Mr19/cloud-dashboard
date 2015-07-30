# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aws_account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvailabilityZone',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Ec2Ami',
            fields=[
                ('ami_id', models.CharField(max_length=15, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('owner_alias', models.CharField(max_length=255, null=True)),
                ('owner_id', models.CharField(max_length=255)),
                ('platform', models.CharField(max_length=255, null=True)),
                ('root_device_name', models.CharField(max_length=255)),
                ('root_device_type', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=255)),
                ('aws_account', models.ForeignKey(to='aws_account.AwsAccount')),
            ],
        ),
        migrations.CreateModel(
            name='Ec2ElasticIp',
            fields=[
                ('public_ip', models.GenericIPAddressField(primary_key=True, serialize=False)),
                ('allocation_id', models.CharField(max_length=255, null=True)),
                ('association_id', models.CharField(max_length=255, null=True)),
                ('domain', models.CharField(max_length=255, choices=[('standard', 'standard'), ('vpc', 'vpc')])),
                ('network_interface_id', models.CharField(max_length=255, null=True)),
                ('network_interface_owner_id', models.CharField(max_length=255, null=True)),
                ('private_ip_address', models.GenericIPAddressField(null=True)),
                ('aws_account', models.ForeignKey(to='aws_account.AwsAccount')),
            ],
        ),
        migrations.CreateModel(
            name='Ec2Instance',
            fields=[
                ('id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('architecture', models.CharField(max_length=255)),
                ('ec2_platform', models.CharField(max_length=255, choices=[('linux', 'linux'), ('mswin', 'mswin'), ('mswinSQL', 'mswinSQL'), ('mswinSQLWeb', 'mswinSQLWeb'), ('windows-unknown', 'windows-unknown')])),
                ('instance_type', models.CharField(max_length=255, choices=[('t2.micro', 't2.micro'), ('t2.small', 't2.small'), ('t2.medium', 't2.medium'), ('m3.medium', 'm3.medium'), ('m3.large', 'm3.large'), ('m3.xlarge', 'm3.xlarge'), ('m3.2xlarge', 'm3.2xlarge'), ('c4.large', 'c4.large'), ('c4.xlarge', 'c4.xlarge'), ('c4.2xlarge', 'c4.2xlarge'), ('c4.4xlarge', 'c4.4xlarge'), ('c4.8xlarge', 'c4.8xlarge'), ('c3.large', 'c3.large'), ('c3.xlarge', 'c3.xlarge'), ('c3.2xlarge', 'c3.2xlarge'), ('c3.4xlarge', 'c3.4xlarge'), ('c3.8xlarge', 'c3.8xlarge'), ('g2.2xlarge', 'g2.2xlarge'), ('r3.large', 'r3.large'), ('r3.xlarge', 'r3.xlarge'), ('r3.2xlarge', 'r3.2xlarge'), ('r3.4xlarge', 'r3.4xlarge'), ('r3.8xlarge', 'r3.8xlarge'), ('i2.xlarge', 'i2.xlarge'), ('i2.2xlarge', 'i2.2xlarge'), ('i2.4xlarge', 'i2.4xlarge'), ('i2.8xlarge', 'i2.8xlarge'), ('d2.xlarge', 'd2.xlarge'), ('d2.2xlarge', 'd2.2xlarge'), ('d2.4xlarge', 'd2.4xlarge'), ('d2.8xlarge', 'd2.8xlarge')])),
                ('kernel', models.CharField(max_length=255, null=True)),
                ('launch_time', models.DateTimeField()),
                ('platform', models.CharField(max_length=255, null=True)),
                ('public_dns_name', models.CharField(max_length=255, null=True)),
                ('state', models.CharField(max_length=255, choices=[('pending', 'pending'), ('running', 'running'), ('shutting-down', 'shutting-down'), ('terminated', 'terminated'), ('stopping', 'stopping'), ('stopped', 'stopped')])),
                ('availability_zone', models.ForeignKey(to='dashboard.AvailabilityZone', null=True)),
                ('aws_account', models.ForeignKey(to='aws_account.AwsAccount')),
            ],
        ),
        migrations.CreateModel(
            name='Ec2Keypair',
            fields=[
                ('key_name', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('fingerprint', models.CharField(max_length=255)),
                ('aws_account', models.ForeignKey(to='aws_account.AwsAccount')),
            ],
        ),
        migrations.CreateModel(
            name='Ec2LoadBalancer',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('created_time', models.DateTimeField()),
                ('dns_name', models.CharField(max_length=255)),
                ('availability_zones', models.ManyToManyField(to='dashboard.AvailabilityZone')),
                ('aws_account', models.ForeignKey(to='aws_account.AwsAccount', null=True)),
                ('instances', models.ManyToManyField(to='dashboard.Ec2Instance')),
            ],
        ),
        migrations.CreateModel(
            name='Ec2Price',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('ec2_platform', models.CharField(max_length=11)),
                ('hourly_price', models.DecimalField(decimal_places=3, max_digits=5, null=True)),
                ('instance_type', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Ec2SecurityGroup',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('owner_id', models.CharField(max_length=255)),
                ('aws_account', models.ForeignKey(to='aws_account.AwsAccount')),
            ],
        ),
        migrations.CreateModel(
            name='Ec2Snapshot',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=255)),
                ('encrypted', models.NullBooleanField(default=False)),
                ('owner_alias', models.CharField(max_length=255, null=True)),
                ('owner_id', models.CharField(max_length=255)),
                ('size', models.IntegerField(null=True)),
                ('start_time', models.DateTimeField(null=True)),
                ('status', models.CharField(max_length=255)),
                ('aws_account', models.ForeignKey(to='aws_account.AwsAccount', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ec2Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('key', models.CharField(max_length=255)),
                ('value', models.CharField(max_length=255)),
                ('aws_account', models.ForeignKey(to='aws_account.AwsAccount')),
            ],
        ),
        migrations.CreateModel(
            name='Ec2Volume',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('attach_time', models.DateTimeField(null=True)),
                ('delete_on_termination', models.BooleanField(default=False)),
                ('create_time', models.DateTimeField(null=True)),
                ('encrypted', models.NullBooleanField(default=False)),
                ('size', models.IntegerField(null=True)),
                ('type', models.CharField(max_length=255)),
                ('availability_zone', models.ForeignKey(to='dashboard.AvailabilityZone', null=True)),
                ('aws_account', models.ForeignKey(to='aws_account.AwsAccount')),
                ('created_from_snapshot', models.ForeignKey(to='dashboard.Ec2Snapshot', blank=True, null=True)),
                ('instance_id', models.ForeignKey(to='dashboard.Ec2Instance', blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('tags', models.ManyToManyField(to='dashboard.Ec2Tag', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('region_name', models.CharField(max_length=255, choices=[('us-east-1', 'US East (N. Virginia)'), ('us-west-2', 'US West (Oregon)'), ('us-west-1', 'US West (N. California)'), ('eu-west-1', 'EU (Ireland)'), ('eu-central-1', 'EU (Frankfurt)'), ('ap-southeast-1', 'Asia Pacific (Singapore)'), ('ap-southeast-2', 'Asia Pacific (Sydney)'), ('ap-northeast-1', 'Asia Pacific (Tokyo)'), ('sa-east-1', 'South America (Sao Paulo)')], serialize=False, primary_key=True)),
            ],
            options={
                'ordering': ['region_name'],
            },
        ),
        migrations.AddField(
            model_name='ec2tag',
            name='region',
            field=models.ForeignKey(to='dashboard.Region'),
        ),
        migrations.AddField(
            model_name='ec2snapshot',
            name='created_from_volume',
            field=models.ForeignKey(to='dashboard.Ec2Volume', null=True),
        ),
        migrations.AddField(
            model_name='ec2snapshot',
            name='region',
            field=models.ForeignKey(to='dashboard.Region'),
        ),
        migrations.AddField(
            model_name='ec2snapshot',
            name='tags',
            field=models.ManyToManyField(to='dashboard.Ec2Tag', blank=True),
        ),
        migrations.AddField(
            model_name='ec2securitygroup',
            name='region',
            field=models.ForeignKey(to='dashboard.Region'),
        ),
        migrations.AddField(
            model_name='ec2securitygroup',
            name='tags',
            field=models.ManyToManyField(to='dashboard.Ec2Tag', blank=True),
        ),
        migrations.AddField(
            model_name='ec2price',
            name='region',
            field=models.ForeignKey(to='dashboard.Region'),
        ),
        migrations.AddField(
            model_name='ec2loadbalancer',
            name='region',
            field=models.ForeignKey(to='dashboard.Region', null=True),
        ),
        migrations.AddField(
            model_name='ec2loadbalancer',
            name='security_groups',
            field=models.ManyToManyField(to='dashboard.Ec2SecurityGroup'),
        ),
        migrations.AddField(
            model_name='ec2loadbalancer',
            name='tags',
            field=models.ManyToManyField(to='dashboard.Ec2Tag'),
        ),
        migrations.AddField(
            model_name='ec2keypair',
            name='region',
            field=models.ForeignKey(to='dashboard.Region'),
        ),
        migrations.AddField(
            model_name='ec2instance',
            name='ec2_price',
            field=models.ForeignKey(to='dashboard.Ec2Price', null=True),
        ),
        migrations.AddField(
            model_name='ec2instance',
            name='image_id',
            field=models.ForeignKey(default=None, to='dashboard.Ec2Ami', null=True),
        ),
        migrations.AddField(
            model_name='ec2instance',
            name='key_name',
            field=models.ForeignKey(to='dashboard.Ec2Keypair', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ec2instance',
            name='security_groups',
            field=models.ManyToManyField(to='dashboard.Ec2SecurityGroup'),
        ),
        migrations.AddField(
            model_name='ec2instance',
            name='tags',
            field=models.ManyToManyField(to='dashboard.Ec2Tag', blank=True),
        ),
        migrations.AddField(
            model_name='ec2elasticip',
            name='instance_id',
            field=models.OneToOneField(to='dashboard.Ec2Instance', null=True),
        ),
        migrations.AddField(
            model_name='ec2elasticip',
            name='region',
            field=models.ForeignKey(to='dashboard.Region'),
        ),
        migrations.AddField(
            model_name='ec2ami',
            name='created_from_snapshot',
            field=models.ForeignKey(to='dashboard.Ec2Snapshot', null=True),
        ),
        migrations.AddField(
            model_name='ec2ami',
            name='region',
            field=models.ForeignKey(to='dashboard.Region', null=True),
        ),
        migrations.AddField(
            model_name='ec2ami',
            name='tags',
            field=models.ManyToManyField(to='dashboard.Ec2Tag', blank=True),
        ),
        migrations.AddField(
            model_name='availabilityzone',
            name='region',
            field=models.ForeignKey(to='dashboard.Region'),
        ),
    ]
