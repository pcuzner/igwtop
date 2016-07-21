#!/usr/bin/env python

# get the lrbd.conf object and parse it
# returning the object to the caller

from config.generic import Config

class GatewayConfig(object):
    """ Configuration of the gateways, based on current state
    """
    def __init__(self, runtime_opts):

        if runtime_opts.test:
            self.gateways = ['localhost']
            self.diskmap = {'sda': 'client-2', 'sdb': 'client-1', 'sdc': 'client-3', 'sdd': 'client-4'}
        else:
            self._read_conf()

        self.client_count = self._unique_clients()

    def _read_conf(self):
        self.gateways = []
        self.diskmap = {}


    def _unique_clients(self):
        return len(set(self.diskmap.values()))

    def refresh(self):
        pass


def get_gateway_info(opts):

    config = GatewayConfig(opts)

    return config