#!/usr/bin/env python

import random
import subprocess
import json

from rtslib_fb import root
from ceph_iscsi_gw.common import Config

def add_rbd_maps(devices):

    rbd_str = subprocess.check_output('rbd showmapped --format=json', shell=True)
    rbd_dict = json.loads(rbd_str)      # make a dict

    for key in rbd_dict:
        dev_id = rbd_dict[key]['device'].split('/')[-1]
        devices[dev_id]['pool-image'] = '{}/{}'.format(rbd_dict[key]['pool'], rbd_dict[key]['name'])


class GatewayConfig(object):
    """ Configuration of the gateways, based on current state
    """
    def __init__(self, logger, runtime_opts, devices):

        self.gateways = []      # list of gateway names
        self.diskmap = {}       # dict - device, pointing to client shortname
        self.client_count = 0   # default count of clients connected to the gateway cluster

        self.config = None      # config object from the rados config object
        self.error = False      # error flag

        # when setting the environment up, 1st allow for overrides
        # TEST mode
        if runtime_opts.test:
            # use some test names and make up some clients
            self.gateways = ['localhost','eric']
            self.diskmap = self._disk2client_mangler(devices)
        #
        # gateway name overrides
        elif runtime_opts.gateways:
            # use the gateway names provided
            self.gateways = runtime_opts.gateways.split(',')
        #
        # default - use the config object stored by igw-ceph-ansible modules
        else:
            # use the config object
            if runtime_opts.config:
                cfg_pool, cfg_obj = runtime_opts.config.split('/')
                self.config = Config(logger, cfg_name=cfg_obj, pool=cfg_pool)

            gw_config = Config(logger)
            if gw_config.error:
                logger.debug("Unable to read the config object")
                self.error = True
            else:
                # the config object is OK, so get the gateway information
                self.gateways = gw_config.config['gateways'].keys()
                if not self.gateways:
                    self.error = True

        if not self.error:
            self.diskmap = self._get_mapped_disks()
            self.client_count = self._unique_clients()

    def _get_mapped_disks(self):
        map = {}
        lio_root = root.RTSRoot()

        for m_lun in lio_root.mapped_luns:
            client_iqn = m_lun.node_wwn
            client_shortname = client_iqn.split(':')[-1]
            image_name = m_lun.tpg_lun.storage_object.name
            udev_path = m_lun.tpg_lun.storage_object.udev_path
            dev_id = udev_path.split('/')[-1]
            map[dev_id] = client_shortname

        return map

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
        # determine the number of unique client names in the disk -> client dict
        return len(set(self.diskmap.values()))

    def refresh(self):
        pass


def get_gateway_info(logger, opts, devices):

    config = GatewayConfig(logger, opts, devices)

    return config