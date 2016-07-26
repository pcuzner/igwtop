#!/usr/bin/env python
__author__ = 'paul'

from time import localtime,strftime

from config.generic import DiskSummary, HostSummary


def summarize(config, pcp_threads):
    dev_stats = {}
    timestamps = set()
    gw_stats = HostSummary()
    first_pass = True

    for dev in config.devices:

        summary = DiskSummary()
        summary.disk_size = config.devices[dev]['size']

        for collector in pcp_threads:

            if dev in collector.metrics.disk_stats:
                summary.reads.append(collector.metrics.disk_stats[dev].read)
                summary.writes.append(collector.metrics.disk_stats[dev].write)
                summary.readkb.append(collector.metrics.disk_stats[dev].readkb)
                summary.writekb.append(collector.metrics.disk_stats[dev].writekb)
                summary.await.append(collector.metrics.disk_stats[dev].await)
                summary.r_await.append(collector.metrics.disk_stats[dev].r_await)
                summary.w_await.append(collector.metrics.disk_stats[dev].w_await)

            if first_pass:
                gw_stats.cpu_busy.append(collector.metrics.cpu_busy_pct)
                gw_stats.net_in.append(collector.metrics.nic_bytes['in'])
                gw_stats.net_out.append(collector.metrics.nic_bytes['out'])
                if collector.metrics.timestamp is not None:
                    timestamps.add(collector.metrics.timestamp)

        first_pass = False

        summary.tot_reads = sum(summary.reads) if len(summary.reads) > 0 else 0
        summary.tot_writes = sum(summary.writes) if len(summary.writes) > 0 else 0
        summary.tot_readkb = sum(summary.readkb) if len(summary.readkb) > 0 else 0
        summary.tot_writekb = sum(summary.writekb) if len(summary.writekb) > 0 else 0
        summary.max_await = max(summary.await) if len(summary.await) > 0 else 0
        summary.max_r_await = max(summary.r_await) if len(summary.r_await) > 0 else 0
        summary.max_w_await = max(summary.w_await) if len(summary.w_await) > 0 else 0

        dev_stats[dev] = summary
        gw_stats.total_capacity += int(summary.disk_size)
        gw_stats.total_iops += int(summary.tot_reads + summary.tot_writes)

    gw_stats.total_net_in = sum(gw_stats.net_in)
    gw_stats.total_net_out = sum(gw_stats.net_out)
    gw_stats.min_cpu = min(gw_stats.cpu_busy)
    gw_stats.max_cpu = max(gw_stats.cpu_busy)

    num_timestamps = len(timestamps)
    if num_timestamps == 0:
        # print num_timestamps
        # first iteration - just use the current time stamp
        gw_stats.timestamp = 'NO DATA'
        # gw_stats.timestamp = strftime('%X',localtime())
    elif num_timestamps == 1:
        # all timestamps from threads are in sync
        dt_parts = str(list(timestamps)[0]).split()
        gw_stats.timestamp = dt_parts[3]
    else:
        # FIXME - likely data issue, since timestamps across threads are different
        gw_stats.timestamp = "Time Skew"

    return gw_stats, dev_stats
