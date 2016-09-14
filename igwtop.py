#!/usr/bin/env python

import argparse
from ConfigParser import ConfigParser
import time
# import pkgutil
import sys
import logging
import os

from threading import Event

from collectors.pcp_provider import PCPcollector
from config.generic import Config
from config.local import get_device_info
from config.lio import get_gateway_info
from igwtopUI.textmode import TextMode

# Supported config file locations/names
CFG_FILES = ['/etc/igwtop.rc',
             os.path.join(os.path.expanduser('~'), '.igwtop.rc')
             ]


def main():
    config = Config()
    config.opts = options
    config.devices = get_device_info()

    if not config.devices:
        print "Error: No devices have been detected on this host, unable to continue"
        sys.exit(12)

    config.gateway_config = get_gateway_info(options)
    if config.gateway_config.error:
        # Problem determining the environment, so abort
        print "Error: Unable to determine the gateway configuration"
        sys.exit(12)

    config.sample_interval = options.interval
    collector_threads = []
    sync_point = Event()
    sync_point.clear()

    if options.debug:
        if options.gateways:
            print "Using gateway names from the config file(s)/run time parameters"
        else:
            print "Using gateway names from the configuration object defined by the ansible modules"

        logger.info("Attempting to open connections to pmcd daemons on the {}"
                    " gateway node(s) ({})".format(len(config.gateway_config.gateways),
                                                 ','.join(config.gateway_config.gateways)))

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

        if options.mode == 'text':
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
        logger.critical("Unable to continue, no pmcd's are available on the gateways to connect to. "
                        "Is pmcd running on the gateways?")


def get_options():

    # establish the defaults based on any present config file(s) config section
    defaults = {}
    config = ConfigParser()
    dataset = config.read(CFG_FILES)
    if len(dataset) > 0:
        if config.has_section("config"):
            defaults.update(dict(config.items("config")))
        else:
            print("Config file detected, but the format is not supported. Ensure the file has a single "
                  "section [config], and declares settings like 'gateways' or 'interval'")
            sys.exit(12)
    else:
        # no config files detected, to seed the run time options
        pass

    # Set up the runtime overrides, any of these could be provided by the cfg file(s)
    parser = argparse.ArgumentParser(prog='igwtop', description='Show iSCSI gateway performance metrics')
    parser.add_argument('-c', '--config-object', type=str,
                        help='pool and object name holding the gateway config object (pool/object_name)')
    parser.add_argument('-g', '--gateways', type=str,
                        help='comma separated iscsi gateway server names')
    parser.add_argument('-i', '--interval', type=int,
                        help='monitoring interval (secs)', choices=range(1, 10))
    parser.add_argument('-d', '--debug', action='store_true', default=False,
                        help='run with additional debug')
    parser.add_argument('-m', '--mode', type=str,
                        choices=(['text']),
                        help='output mode')
    # parser.add_argument('-t', '--test', action='store_true', default=False,
    #                     help='run in test mode - i.e. without rados interaction')

    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.5')

    # use the defaults dict for the options
    parser.set_defaults(**defaults)

    # create the opts object which combines the defaults from the config file(s) + runtime overrides
    opts = parser.parse_args()

    # establish defaults, just in case they're missing from the config file(s) AND run time call
    if not opts.interval:
        opts.interval = 1
    if not opts.mode:
        opts.mode = 'text'
    if not opts.config_object:
        opts.config_object = 'rbd/gateway.conf'

    return opts


if __name__ == '__main__':
    options = get_options()

    # define logging to the console
    # set the format to just the msg
    logger = logging.getLogger("igwtop")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()

    if options.debug:
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)

    fmt = logging.Formatter('%(message)s')
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # validate opts, then
    main()
