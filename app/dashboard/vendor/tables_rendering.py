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


from django.utils.html import format_html
from django.db.models.manager import Manager
from django.db.models.query import QuerySet

from cloud_dashboard.common.utils.prices import compute_resource_price_class

__author__ = 'Arnaud Desclouds <arnaud.software@use.startmail.com>'


class BackgroundColors(object):
    values = ['#92B5F2',
              '#83AAF1',
              '#74A0EF',
              '#6495ED',
              '#5A86D5',
              '#5077BE',
              '#4668A6',
              '#3C598E',
              '#324A76',
              '#283C5F']


class CustomColumnRendering(object):
    @staticmethod
    def render_selected_resources(record, context_dict):
        """Renders the chexbox column.

        Checks if a resource is selected and renders its checkbox checked
        or not accordingly. The context_dict contains as keys the names of
        the resources that have links to some resources of the class of the
        record object, record can have links or not to the resources contained
        in context_dict, if it has links it will render a checked checkboxes,
        otherwise not.

        Args:
            record: The record that will be selected or not.
            context_dict: The dictionary containing the origin resources that
                linked to that page.

        Returns:
            A checkbox checked or not depending if the record contains a
            dependency to the resources contained in context_dict.
        """
        for k, v in context_dict.items():
            if k and v:
                if isinstance(v, QuerySet) and k in [str(o.pk) for o in
                                                     v] or not isinstance(v,
                                                                          QuerySet) and k == v.pk:
                    return format_html(
                        '<input name="selected_{}" type="checkbox" value="{}" checked>',
                        type(record).__name__.lower(),
                        record.pk)
        return format_html(
            '<input name="selected_{}" type="checkbox" value="{}">',
            type(record).__name__.lower(),
            record.pk)

    @staticmethod
    def render_attribute(record, record_attribute, empty=None,
                         custom_param_name=None):
        """Renders a link to linked resources.

        If the record possesses an attribute represented by record_attribute
        being either a foreign key or a related set then its value is showed
        in a link to its corresponding table. That link passes as parameter
        name the record class name in lowercase without the 'ec2' prefix and
        as parameter value the primary key of the record, that allows to
        easily identify the origin resource after clicking on the link.

        Args:
            record: The origin record from which the link is created.
            record_attribute: A foreign key or a related set to render.
            empty: If no record_attribute is found the value to show instead
                of None.
            custom_param_name: A custom parameter name to use instead of the
                record class name in lowercase without the 'ec2' prefix.
                Can be useful if the same origin resource links to a
                 record_attribute with different relation types.

        Returns:
            A link to the linked resources with as parameter name the record
            class name in lowercase without the 'ec2' prefix and as parameter
            value the primary key of the record.

            If no linked resources are found returns None.
        """
        source_class_name = record.__class__.__name__.lower()
        param_name = custom_param_name or source_class_name[3:] + '_id'

        if issubclass(record_attribute.__class__, Manager):
            dest_class_name = record_attribute.first().__class__.__name__.lower()
            url = dest_class_name + 's'
            if record_attribute.exists():
                return format_html('<a href=/{}/?{}={}>{}</a>',
                                   url,
                                   param_name,
                                   record.pk,
                                   str([o.pk for o in record_attribute.all()]))
        elif record_attribute:
            dest_class_name = record_attribute.__class__.__name__.lower()
            url = dest_class_name + 's'
            return format_html('<a href=/{}/?{}={}>{}</a>',
                               url,
                               param_name,
                               record.pk,
                               record_attribute.pk)
        return empty

    @staticmethod
    def render_tags(record):
        """Renders the tags attribute of a resource.

        Renders a link to the tags's table with values the tags of the resource
        represented by record.
        The link value contains the tags keys and values each in a <span>
        HTML tag. The resource origin class name in lowercase without the
        'ec2' prefix is the parameter name and the parameter value is its
        primary key, allowing to easily identify the origin resource.

        Args:
            record: The origin resource possessing the tags to render.

        Returns:
            A link as described below or an empty string if the resource has
            no tags.
        """
        tags = ''
        if record.tags.exists():
            tags = '<a href=/ec2tags/?{}_id={}>['.format(
                record.__class__.__name__.lower()[3:],
                record.pk)
            for tag in record.tags.all():
                tags += '<span>\'{}\'</span>:<span>\'{}\'</span><br>'.format(
                    tag.key,
                    tag.value)
            tags = tags[:len(tags) - 4]  # Removes the last <br>
            tags += ']</a>'
        return format_html(tags)

    @staticmethod
    def render_background_color(resource):
        """Returns the background color of a resource based on its price class.

        Computes the resource price class and returns an hexadecimal color name
        to be used as background color for the resource's price column.

        Args:
            resource: A resource instance.

        Returns:
            An hexadecimal color name based on the resource price class or
            None if the resource doesn't belong to a price class.
        """
        resource_class = compute_resource_price_class(resource)
        if resource_class == None:
            return None
        else:
            return BackgroundColors.values[resource_class]
