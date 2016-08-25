#!/usr/bin/env python

import argparse
import time
import pkgutil
import sys
import logging

from threading import Event

from collectors.pcp_provider import PCPcollector
from config.generic import Config
from config.local import get_device_info
from config.ceph import get_gateway_info
from igwtopUI.textmode import TextMode


def main():

    gw_config_pkg = pkgutil.find_loader('ceph_iscsi_gw')
    if gw_config_pkg is None and not opts.gateways:
        print("Unable to determine the gateways - package ceph_iscsi_gw is not installed, and "
              "you have\nnot provided the gateway nodes names using the -g option")
        sys.exit(12)

    config = Config()
    config.opts = opts
    config.devices = get_device_info()

    config.gateway_config = get_gateway_info(logger, opts, config.devices)
    if config.gateway_config.error:
        # Problem determining the environment, so abort
        logger.error("Error: Unable to determine the gateway configuration")
        sys.exit(12)

    config.sample_interval = opts.interval
    collector_threads = []
    sync_point = Event()
    sync_point.clear()
    logger.info("Attempting to open connections to pmcd daemons on the gateway nodes")

    # NB. interval must be a string, defaulting to 1 for testing
    for gw in config.gateway_config.gateways:
        collector = PCPcollector(logger, sync_point, host=gw, interval=config.sample_interval)

        if collector.connected:
            collector.daemon = True
            collector.start()
            collector_threads.append(collector)
        else:
            del collector
            logger.error("Error: Unable to connect to pmcd daemon on {}".format(gw))

    # Continue as long as we have at least 1 collector connected to a host's pmcd
    if len(collector_threads) > 0:

        sync_point.set()

        if opts.mode == 'text':
            interface = TextMode(config, collector_threads)
            interface.daemon = True

        interface.start()

        try:
            # wait until the interface thread exits
            while interface.isAlive():
                time.sleep(0.2)
        except KeyboardInterrupt:
            # reset the terminal settings
            interface.reset()
    else:
        logger.critical("Unable to continue, no pmcd's are available on the gateways to connect to")

def get_options():
    parser = argparse.ArgumentParser(prog='igwtop', description='Show iSCSI gateway performance metrics')
    parser.add_argument('-c', '--config', type=str,
                        help='pool and object name holding the gateway config object (pool/object_name)')
    parser.add_argument('-g', '--gateways', type=str,
                        help='iscsi gateway server names (overrides the config object)')
    parser.add_argument('-i', '--interval', type=int, default=1,
                        help='monitoring interval (secs)', choices=range(1, 10))
    parser.add_argument('-d', '--debug', action='store_true', default=False,
                        help='run with additional debug logging (NOT IMPLEMENTED YET)')
    parser.add_argument('-m', '--mode', type=str, default='text',
                        choices=(['text']),
                        help='output mode')
    parser.add_argument('-t', '--test', action='store_true', default=False,
                        help='run in test mode - i.e. without rados interaction')

    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.5')
    opts = parser.parse_args()
    return opts

if __name__ == '__main__':
    opts = get_options()

    # define logging to the console
    # set the format to just the msg
    logger = logging.getLogger("igwtop")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()

    if opts.debug:
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)

    fmt = logging.Formatter('%(message)s')
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # validate opts, then
    main()
