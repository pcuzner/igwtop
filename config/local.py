#!/usr/bin/env python

# get the disks available on this host
# filter for rbd devices and return a dict of
# disk objects to the caller
import subprocess
import json


def str2dict(kv_string, dict_key):

    ret_dict = {}
    members = []
    for dev in kv_string.split('\n'):
        s = ''
        for pair in dev.split():
            k, v = pair.split('=')
            s += '"{}": {}, '.format(k.lower(), v)

        s = '{{ {} }}'.format(s[:-2])               # drop hanging ','
        d = json.loads(s)
        members.append(d)

    ret_dict[dict_key] = members[:-1]               # drop last empty member
    return ret_dict


def get_device_info():
    """ Assuming all devices are mapped to all gateways, we can just
        query the localhost for device information that can later be
        combined with the metrics returned from pcp
    """
    device_blacklist = ('sr', 'vd')
    device_data = {}
    # for upstream lsblk version 2.28, it's simpler to use -J to go straight to json
    # lsblk_out = subprocess.check_output('lsblk -d -S -b -J -o NAME,SIZE,ROTA,TYPE', shell=True)

    # however, for downstream util-linux version is 2.23 doesn't have -J, so use -P instead
    lsblk_out = subprocess.check_output('lsblk -d -b -P -o NAME,SIZE,ROTA', shell=True)
    blk_data = str2dict(lsblk_out, 'blockdevices')

    for dev_dict in blk_data['blockdevices']:
        dev_name = dev_dict['name']
        if dev_name.startswith(device_blacklist):
            continue
        del dev_dict['name']
        device_data[dev_name] = dev_dict

    return device_data
