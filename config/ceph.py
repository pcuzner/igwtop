#!/usr/bin/env python

# get the lrbd.conf object and parse it
# returning the object to the caller
import random
import subprocess
import json


def add_rbd_maps(devices):

    rbd_str = subprocess.check_output('rbd showmapped --format=json', shell=True)
    rbd_dict = json.loads(rbd_str)      # make a dict

    for key in rbd_dict:
        dev_id = rbd_dict[key]['device'].split('/')[-1]
        devices[dev_id]['pool-image'] = '{}/{}'.format(rbd_dict[key]['pool'], rbd_dict[key]['name'])


class GatewayConfig(object):
    """ Configuration of the gateways, based on current state
    """
    def __init__(self, runtime_opts, devices):

        if runtime_opts.test:
            self.gateways = ['localhost','eric']
            self.diskmap = self._disk2client_mangler(devices)

        else:
            self._read_conf()

        self.client_count = self._unique_clients()




    def _read_conf(self):
        self.gateways = []
        self.diskmap = {}

    def _disk2client_mangler(self, devices):
        map = {}
        client_pfx = 'client-'
        client_sfx = random.sample(xrange(len(devices)*10), len(devices))
        ptr = 0
        for devname in devices:
            map[devname] = client_pfx + str(client_sfx[ptr])
            ptr += 1

        return map

    def _unique_clients(self):
        return len(set(self.diskmap.values()))

    def refresh(self):
        pass


def get_gateway_info(opts, devices):

    config = GatewayConfig(opts, devices)

    return config