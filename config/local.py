#!/usr/bin/env python

# get the disks available on this host
# filter for rbd devices and return a dict of
# disk objects to the caller
import subprocess
import json

def get_device_info():
    """ Assuming all devices are mapped to all gateways, we can just
        query the localhost for device information that can later be
        combined with the metrics returned from pcp
    """
    device_blacklist = ['sr0']
    device_data = {}
    lsblk_out = subprocess.check_output('lsblk -d -S -b -J -o NAME,SIZE,ROTA,TYPE', shell=True)
    blk_data = json.loads(lsblk_out)

    for dev_dict in blk_data['blockdevices']:
        dev_name = dev_dict['name']
        if dev_name in device_blacklist:
            continue
        del dev_dict['name']
        device_data[dev_name] = dev_dict

    # print "Device info:"
    # print str(device_data)

    return device_data