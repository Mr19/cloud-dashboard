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


from django.test import TestCase
from django.contrib.auth.models import User

from aws_account.models import AwsAccount

from aws_account.models import AwsUser

__author__ = 'Arnaud Desclouds <arnaud.software@use.startmail.com>'

class AwsAccountTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.accounts = []
        for i in range(0, 4):
            name = 'a-{}'.format(i)
            aws_access_key_id = 'access-key-id-{}'.format(i)
            aws_secret_access_key = 'aws-secret-access-key-{}'.format(i)
            cls.accounts.append(AwsAccount.objects.create(name=name,
                                                          aws_access_key_id=aws_access_key_id,
                                                          aws_secret_access_key=aws_secret_access_key))

        cls.users = []
        cls.aws_users = []
        for i in range(0, 4):
            username = 'username-{}'.format(i)
            password = 'password-{}'.format(i)
            user = User.objects.create_user(username=username,
                                            password=password)
            cls.users.append(user)
            cls.aws_users.append(AwsUser.objects.get(user=user))

    def test_create_user_signal(self):
        users = [aws_user.user for aws_user in self.aws_users]
        self.assertEqual(self.users, users)

    def test_aws_user_add_aws_account(self):
        for i, aws_user in enumerate(self.aws_users):
            aws_user.aws_accounts.add(self.accounts[i])
        for i, aws_user in enumerate(self.aws_users):
            self.assertEqual([o.pk for o in aws_user.aws_accounts.all()],
                             [self.accounts[i].pk])

    def test_shared_aws_account_creation(self):
        for aws_user in self.aws_users:
            aws_user.aws_accounts.add(*self.accounts)
        for i, val1 in enumerate(self.aws_users):
            for j, val2 in enumerate(self.aws_users):
                self.assertEqual(list(self.aws_users[i].aws_accounts.all()),
                                 list(self.aws_users[j].aws_accounts.all()))


class AwsAccountClientTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.username = 'jane'
        cls.password = 'password1'
        User.objects.create_user(cls.username, password=cls.password)

    def test_login(self):
        response = self.client.post('/login/',
                                    {'username': self.username,
                                     'password': self.password},
                                    secure=True)
        self.assertEqual(response.status_code, 302)

    def test_create_aws_account(self):
        name = 'account-1'
        aws_access_key_id = 'ACCESS-KEY-1'
        aws_secret_access_key = 'SECRET-ACCESS-KEY-1'
        aws_account = None
        try:
            aws_account = AwsAccount.objects.get(name=name,
                                             aws_access_key_id=aws_access_key_id,
                                             aws_secret_access_key=aws_secret_access_key)
        except AwsAccount.DoesNotExist:
            pass
        self.assertIsNone(aws_account)

        self.client.post('/login/',
                         {'username': self.username,
                          'password': self.password},
                         secure=True)

        response = self.client.post('/aws-accounts/add/',
                                    {'name': name,
                                     'aws_access_key_id': aws_access_key_id,
                                     'aws_secret_access_key': aws_secret_access_key})
        self.assertEqual(response.status_code, 302)

        aws_account = AwsAccount.objects.get(name=name,
                                             aws_access_key_id=aws_access_key_id,
                                             aws_secret_access_key=aws_secret_access_key)
        self.assertIsNotNone(aws_account)

