#!/usr/bin/env python


class Config(object):
    """ simple object to hold the current configuration across the gateways
    """

    def __repr__(self):
        return str(self.__dict__)


class DiskMetrics(object):

    def __repr__(self):
        return str(self.__dict__)


class HostSummary(object):

    def __init__(self):
        self.cpu_busy = []
        self.net_in = []
        self.net_out = []
        self.timestamp = ''
        self.total_capacity = 0
        self.total_iops = 0

    def __repr__(self):
        return str(self.__dict__)


class DiskSummary(object):

    def __init__(self):
        self.reads = []
        self.writes = []
        self.readkb = []
        self.writekb = []
        self.await = []
        self.r_await = []
        self.w_await = []

    def __repr__(self):
        return str(self.__dict__)


class GatewayMetrics(object):

    def __repr__(self):
        return str(self.__dict__)
