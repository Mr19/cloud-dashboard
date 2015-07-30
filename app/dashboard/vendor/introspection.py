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


from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields.related import OneToOneField
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.related import ManyToManyField

__author__ = 'Arnaud Desclouds <arnaud.software@use.startmail.com>'

__RELATIONS = {OneToOneField, ForeignKey, ManyToManyField}


def introspect(boto_obj, django_model):
    """Introspect a boto object and a Django model.

    Introspect a boto object and find the common attributes names belonging
    to the Django model. Returns a dictionary containing those attributes
    and the values found in the boto_obj.
    Primarily used for the update_or_create default parameter of Django models.

    Args:
        boto_obj: A boto object to introspect.
        django_model: A Django model to introspect to find the common
        attributes.

    Returns:
        A dictionary containing the common attributes found in the boto_obj and
        the django_model with as key their names and as values the values found
        in the boto_obj.
    """
    attrs = {}
    for attr in dir(boto_obj):
        try:
            django_model._meta.get_field(attr)
            if type(django_model._meta.get_field(attr)) not in __RELATIONS:
                attrs[attr] = getattr(boto_obj, attr)
        except FieldDoesNotExist:
            continue
    return attrs
