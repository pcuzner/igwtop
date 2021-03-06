#!/usr/bin/env python
__author__ = 'paul'
import time
import threading
import sys

from utils.kbd import TerminalFile
from utils.data import bytes2human
from igwtopUI.datamanager import summarize


class TextMode(threading.Thread):
    """
    Class that provides the text mode of the tool. An object of this
    class runs as a thread
    """

    def __init__(self, config, pcp_threads):
        threading.Thread.__init__(self)
        self.config = config
        self.pcp_collectors = pcp_threads
        self.terminal = None

    def show_stats(self, gw_stats, disk_summary):
        num_gws = len(gw_stats.cpu_busy)
        desc = "Gateways" if num_gws > 1 else "Gateway"

        print("igwtop  {:>2} {:<8}   CPU% MIN:{:>3.0f} MAX:{:>3.0f}    Network Total In:{:>6}"
              "  Out:{:>6}   {}".format(num_gws,
                                        desc,
                                        gw_stats.min_cpu,
                                        gw_stats.max_cpu,
                                        bytes2human(gw_stats.total_net_in),
                                        bytes2human(gw_stats.total_net_out),
                                        gw_stats.timestamp))

        print("Capacity: {:>5}    IOPS: {:>5}   Clients:{:>3}".format(
              bytes2human(gw_stats.total_capacity),
              gw_stats.total_iops,
              self.config.gateway_config.client_count))

        print "Device   Pool/Image        Size     r/s     w/s    rMB/s     wMB/s    await  r_await  w_await  Client"

        # Metrics shown sorted by device name by default (i.e. rbd0..rbd1..rbdX)
        for devname in sorted(disk_summary):

            if devname in self.config.gateway_config.diskmap:
                client = self.config.gateway_config.diskmap[devname]
            else:
                client = ''

            print("{:^6}  {:<16}   {:>4}   {:>5}   {:>5}   {:>6.2f}    {:>6.2f}   {:>6.2f}   {:>6.2f}   "
                  "{:>6.2f}  {:<20}".format(devname,
                                            disk_summary[devname].pool_image,
                                            bytes2human(disk_summary[devname].disk_size),
                                            int(disk_summary[devname].tot_reads),
                                            int(disk_summary[devname].tot_writes),
                                            disk_summary[devname].tot_readkb/1024,
                                            disk_summary[devname].tot_writekb/1024,
                                            disk_summary[devname].max_await,
                                            disk_summary[devname].max_r_await,
                                            disk_summary[devname].max_w_await,
                                            client))
        print


    def reset(self):
        self.terminal.reset()

    def run(self):
        term = TerminalFile(sys.stdin)
        self.terminal = term
        ctr = 0
        loop_delay = 0.5

        while 1:
            try:
                time.sleep(loop_delay)
                ctr += loop_delay
                if ctr == self.config.sample_interval:
                    ctr = 0
                    gw_stats, disk_summary = summarize(self.config, self.pcp_collectors)
                    self.show_stats(gw_stats, disk_summary)
                    del gw_stats
                    del disk_summary

                c = term.getch()
                if c == 'q':
                    break
            except KeyboardInterrupt:
                print "breaking from thread"
                break

        # exit the thread
