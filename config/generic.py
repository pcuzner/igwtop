#!/usr/bin/env python


class Config(object):
    """
    Simple object to hold the current configuration across the gateways
    """

    def __repr__(self):
        return str(self.__dict__)


class DiskMetrics(Config):
    """
    Simple object used to to hold disk metrics
    """


class GatewayMetrics(Config):
    """
    Simple config object
    """


class HostSummary(object):
    """
    Simple object to hold the current configuration across the gateways
    """

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
    """
    Class defining objects providing disk summary statistics
    """

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
