#!/usr/bin/env python

import argparse
import time

from collectors.pcp_provider import PCPcollector
from config.generic import Config
from config.local import get_device_info
from config.ceph import get_gateway_info
from igwtopUI.textmode import TextMode


def main():

    config = Config()
    config.devices = get_device_info()
    config.gateway_config = get_gateway_info(opts, config.devices)
    config.sample_interval = opts.interval
    collector_threads = []

    # NB. interval must be a string, defaulting to 1 for testing
    for gw in config.gateway_config.gateways:
        collector = PCPcollector(host=gw, interval=config.sample_interval)

        if collector.connected:
            collector.daemon = True
            collector.start()
            collector_threads.append(collector)
        else:
            del collector
            print "Error: Unable to connect to pmcd daemon on %s" % gw

    # Continue as long as we have at least 1 collector connected to a host's pmcd
    if len(collector_threads) > 0:

        if opts.mode == 'text':
            interface = TextMode(config, collector_threads)
            interface.daemon = True

        interface.start()

        try:
            # wait until the interface thread exits
            while interface.isAlive():
                time.sleep(0.5)
        except KeyboardInterrupt:
            # reset the terminal settings
            interface.reset()
    else:
        print "Unable to continue, no pmcd's are available on the gateways to connect to"

def get_options():
    parser = argparse.ArgumentParser(prog='igwtop', description='Show iSCSI gateway performance metrics')
    parser.add_argument('-i', '--interval', type=int, default=1,
                        help='monitoring interval (secs)', choices=range(1, 10))
    parser.add_argument('-d', '--debug', action='store_true', default=False,
                        help='run with additional debug logging (NOT IMPLEMENTED YET)')
    parser.add_argument('-m', '--mode', type=str, default='text',
                        choices=(['text']),
                        help='output mode')
    parser.add_argument('-t', '--test', action='store_true', default=True,
                        help='run in test mode - i.e. without rados interaction')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.5')
    opts = parser.parse_args()
    return opts

if __name__ == '__main__':
    opts = get_options()
    # validate opts, then
    main()
