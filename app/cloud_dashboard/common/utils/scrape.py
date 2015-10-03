# Copyright (c) 2013 Garret Heaton (powdahound.com)
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from lxml import etree
import urllib.request, urllib.error, urllib.parse
import re
import json


class Instance(object):
    def __init__(self):
        self.vpc = None
        self.arch = ['x86_64']
        self.ECU = 0
        self.linux_virtualization_types = []
        self.ebs_throughput = 0
        self.ebs_iops = 0

    def to_dict(self):
        d = dict(family=self.family,
                 instance_type=self.instance_type,
                 arch=self.arch,
                 vCPU=self.vCPU,
                 ECU=self.ECU,
                 memory=self.memory,
                 ebs_optimized=self.ebs_optimized,
                 ebs_throughput=self.ebs_throughput,
                 ebs_iops=self.ebs_iops,
                 network_performance=self.network_performance,
                 enhanced_networking=self.enhanced_networking,
                 pricing=self.pricing,
                 vpc=self.vpc,
                 linux_virtualization_types=self.linux_virtualization_types,
                 generation=self.generation)
        if self.ebs_only:
            d['storage'] = None
        else:
            d['storage'] = dict(ssd=self.ssd,
                                devices=self.num_drives,
                                size=self.drive_size)
        return d


def totext(elt):
    s = etree.tostring(elt, method='text', encoding='unicode').strip()
    return re.sub(r'\*\d$', '', s)


def parse_prev_generation_instance(tr):
    i = Instance()
    cols = tr.xpath('td')
    assert len(cols) == 8, "Expected 8 columns in the table, but got %d" % len(cols)
    i.family = totext(cols[0])
    i.instance_type = totext(cols[1])
    archs = totext(cols[2])
    i.arch = []
    if '32-bit' in archs:
        i.arch.append('i386')
    if '64-bit' in archs:
        i.arch.append('x86_64')
    assert i.arch, "No archs detected: %s" % (archs,)
    i.vCPU = int(totext(cols[3]))
    i.memory = float(totext(cols[4]))
    storage = totext(cols[5])
    m = re.search(r'(\d+)\s*x\s*([0-9,]+)?', storage)
    i.ssd = False
    if m:
        i.ebs_only = False
        i.num_drives = int(m.group(1))
        i.drive_size = int(m.group(2).replace(',', ''))
        i.ssd = 'SSD' in totext(cols[5])
    else:
        assert storage == 'EBS Only', "Unrecognized storage spec: %s" % (storage,)
        i.ebs_only = True
    i.ebs_optimized = totext(cols[6]).lower() == 'yes'
    i.network_performance = totext(cols[7])
    i.enhanced_networking = False
    i.generation = 'previous'
    # print "Parsed %s..." % (i.instance_type)
    return i


def parse_instance(tr, inst2family):
    i = Instance()
    cols = tr.xpath('td')
    assert len(cols) == 12, "Expected 12 columns in the table, but got %d" % len(cols)
    i.instance_type = totext(cols[0])
    i.family = inst2family.get(i.instance_type, "Unknown")
    # Some t2 instances support 32-bit arch
    # http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-resize.html#resize-limitations
    if i.instance_type in ('t2.micro', 't2.small'):
        i.arch.append('i386')
    i.vCPU = int(totext(cols[1]))
    i.memory = float(totext(cols[2]))
    storage = totext(cols[3])
    m = re.search(r'(\d+)\s*x\s*([0-9,]+)?', storage)
    i.ssd = False
    if m:
        i.ebs_only = False
        i.num_drives = int(m.group(1))
        i.drive_size = int(m.group(2).replace(',', ''))
        i.ssd = 'SSD' in totext(cols[3])
    else:
        assert storage == 'EBS Only', "Unrecognized storage spec: %s" % (storage,)
        i.ebs_only = True
    i.ebs_optimized = totext(cols[10]).lower() == 'yes'
    i.network_performance = totext(cols[4])
    i.enhanced_networking = totext(cols[11]).lower() == 'yes'
    i.generation = 'current'
    # print "Parsed %s..." % (i.instance_type)
    return i


def _rindex_family(inst2family, details):
    rows = details.xpath('tbody/tr')[0:]
    for r in rows:
        cols = r.xpath('td')
        for i in totext(cols[1]).split('|'):
            i = i.strip()
            inst2family[i] = totext(cols[0])


def scrape_families():
    inst2family = dict()
    tree = etree.parse(urllib.request.urlopen("http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-types.html"), etree.HTMLParser())
    details = tree.xpath('//div[@class="informaltable"]//table')[0]
    hdrs = details.xpath('thead/tr')[0]
    if totext(hdrs[0]).lower() == 'instance family' and 'current generation' in totext(hdrs[1]).lower():
       _rindex_family(inst2family, details)

    details = tree.xpath('//div[@class="informaltable"]//table')[1]
    hdrs = details.xpath('thead/tr')[0]
    if totext(hdrs[0]).lower() == 'instance family' and 'previous generation' in totext(hdrs[1]).lower():
       _rindex_family(inst2family, details)

    assert len(inst2family) > 0, "Failed to find instance family info"
    return inst2family


def scrape_instances():
    inst2family = scrape_families()
    tree = etree.parse(urllib.request.urlopen("http://aws.amazon.com/ec2/instance-types/"), etree.HTMLParser())
    details = tree.xpath('//table')[9]
    rows = details.xpath('tbody/tr')[1:]
    assert len(rows) > 0, "Didn't find any table rows."
    current_gen = [parse_instance(r, inst2family) for r in rows]

    tree = etree.parse(urllib.request.urlopen("http://aws.amazon.com/ec2/previous-generation/"), etree.HTMLParser())
    details = tree.xpath('//table')[6]
    rows = details.xpath('tbody/tr')[1:]
    assert len(rows) > 0, "Didn't find any table rows."
    prev_gen = [parse_prev_generation_instance(r) for r in rows]

    return prev_gen + current_gen



def transform_region(reg):
    region_map = {
        'eu-ireland': 'eu-west-1',
        'eu-frankfurt': 'eu-central-1',
        'apac-sin': 'ap-southeast-1',
        'apac-syd': 'ap-southeast-2',
        'apac-tokyo': 'ap-northeast-1'}
    if reg in region_map:
        return region_map[reg]
    m = re.search(r'^([^0-9]*)(-(\d))?$', reg)
    assert m, "Can't parse region: %s" % (reg,)
    base = m.group(1)
    num = m.group(3) or '1'
    return base + "-" + num


def add_pricing(imap, data, platform):
    for region_spec in data['config']['regions']:
        region = transform_region(region_spec['region'])
        for t_spec in region_spec['instanceTypes']:
            typename = t_spec['type']
            for i_spec in t_spec['sizes']:
                i_type = i_spec['size']
                # As best I can tell, this type doesn't exist, but is
                # in the pricing charts anyways.
                if i_type == 'cc2.4xlarge':
                    continue
                assert i_type in imap, "Unknown instance size: %s" % (i_type, )
                inst = imap[i_type]
                inst.pricing.setdefault(region, {})
                # print "%s/%s" % (region, i_type)
                for col in i_spec['valueColumns']:
                    inst.pricing[region][platform] = col['prices']['USD']

                # ECU is only available here
                ecu = i_spec['ECU']
                if ecu == 'variable':
                    inst.ECU = 0
                else:
                    inst.ECU = float(ecu)


def add_pricing_info(instances):
    for i in instances:
        i.pricing = {}
    by_type = {i.instance_type: i for i in instances}

    for platform in ['linux', 'mswin', 'mswinSQL', 'mswinSQLWeb', 'rhel', 'sles']:
        # current generation
        pricing_url = 'http://a0.awsstatic.com/pricing/1/ec2/%s-od.min.js' % (platform,)
        jsonp_string = urllib.request.urlopen(pricing_url).read().decode()
        json_string = re.sub(r"(\w+):", r'"\1":', jsonp_string[jsonp_string.index('callback(') + 9 : -2]) # convert into valid json
        pricing = json.loads(json_string)
        add_pricing(by_type, pricing, platform)

        # previous generation
        pricing_url = 'http://a0.awsstatic.com/pricing/1/ec2/previous-generation/%s-od.min.js' % (platform,)
        jsonp_string = urllib.request.urlopen(pricing_url).read().decode()
        json_string = re.sub(r"(\w+):", r'"\1":', jsonp_string[jsonp_string.index('callback(') + 9 : -2]) # convert into valid json
        pricing = json.loads(json_string)
        add_pricing(by_type, pricing, platform)



def scrape():
    """Scrape AWS to get instance data"""
    print("Parsing instance types...")
    all_instances = scrape_instances()
    print("Parsing pricing info...")
    add_pricing_info(all_instances)
    return all_instances
