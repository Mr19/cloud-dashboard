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

from django.shortcuts import render
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView
from django.views.decorators.debug import sensitive_post_parameters

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from django_tables2 import SingleTableView

from aws_account.forms import AwsAccountForm
from aws_account.models import AwsAccount
from aws_account.models import AwsUser
from aws_account.tables import AwsAccountTable
from dashboard.vendor.aws_resources_controller import AwsResourcesController

__author__ = 'Arnaud Desclouds <arnaud.software@use.startmail.com>'

@sensitive_post_parameters()
def create_user(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'])

            return HttpResponseRedirect('/login/')
    else:
        form = UserCreationForm()

    return render(request, 'registration/sign-up.html', {'form': form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


@sensitive_post_parameters()
def create_aws_account_view(request):
    if request.method == 'POST':
        aws_user = AwsUser.objects.get(user_id=request.user.id)

        try:
            aws_account = AwsAccount.objects.get(aws_access_key_id=request.POST.get('aws_access_key_id'),
                                                 aws_secret_access_key=request.POST.get('aws_secret_access_key'))
        except AwsAccount.DoesNotExist:
            aws_account = None

        form = AwsAccountForm(request.POST, instance=aws_account)

        if form.is_valid():
            aws_account = form.save()
            aws_user.aws_accounts.add(aws_account)
            # reset resources_last_updated to get resources from new account
            aws_user.resources_last_updated = datetime(1970, month=1, day=1,
                                                   tzinfo=timezone.utc)
            aws_user.save()
            return HttpResponseRedirect('/aws-accounts/')
    else:
        form = AwsAccountForm()


    return render(request, 'aws_account/add_aws_account.html', {'form': form})


def delete_aws_account_view(request, pk):
    aws_account = AwsAccount.objects.get(pk=pk)
    if request.method == 'POST':
        current_user = AwsUser.objects.get(user=request.user)
        current_user.aws_accounts.remove(aws_account)

        if not aws_account.awsuser_set.exists():
            # No remaining users associated to this AwsAccount, we can delete it.
            aws_account.delete()
        return HttpResponseRedirect('/aws-accounts/')
    else:
        return render(request, 'aws_account/awsaccount_confirm_delete.html', {'object': aws_account})


class AwsAccountUpdate(UpdateView):
    model = AwsAccount
    fields = '__all__'
    template_name = 'aws_account/update_aws_account.html'


class AwsAccountTableView(SingleTableView):
    model = AwsAccount
    table_class = AwsAccountTable

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if self.request.GET.get('update_resources') == 'true':
            AwsResourcesController(self.request.user).manually_update_ec2_data()
        elif self.request.GET.get('update_prices') == 'true':
            AwsResourcesController(self.request.user).manually_update_prices()

        return super(AwsAccountTableView, self).dispatch(*args, **kwargs)

    def get_table_data(self):
        return AwsUser.objects.get(user=self.request.user).aws_accounts.all()
