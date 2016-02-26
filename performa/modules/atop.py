#!/usr/bin/python

import os
import re
import tempfile

ATOP_FILE_NAME = os.path.join(tempfile.gettempdir(), 'performa.atop')
UNIQUE_NAME = 'performa_atop'

PREFIX_PATTERN = (
    '(?P<host>\S+)\s+'
    '(?P<timestamp>\d+)\s+'
    '(?P<date>\S+)\s+'
    '(?P<time>\S+)\s+'
    '(?P<interval>\w+)\s+'
)

CPU_TOTAL_PATTERN = re.compile(
    '(?P<label>CPU)\s+' +
    PREFIX_PATTERN +
    '(?P<ticks_per_second>\d+)\s+'
    '(?P<cpu_count>\d+)\s+'
    '(?P<sys_ticks>\d+)\s+'
    '(?P<user_ticks>\d+)\s+'
    '(?P<nice_ticks>\d+)\s+'
    '(?P<idle_ticks>\d+)\s+'
    '(?P<wait_ticks>\d+)\s+'
    '(?P<irq_ticks>\d+)\s+'
    '(?P<softirq_ticks>\d+)\s+'
    '(?P<steal_ticks>\d+)\s+'
    '(?P<guest_ticks>\d+)',
)

CPU_PATTERN = re.compile(
    '(?P<label>cpu)\s+' +
    PREFIX_PATTERN +
    '(?P<ticks_per_second>\d+)\s+'
    '(?P<cpu_id>\d+)\s+'
    '(?P<sys_ticks>\d+)\s+'
    '(?P<user_ticks>\d+)\s+'
    '(?P<nice_ticks>\d+)\s+'
    '(?P<idle_ticks>\d+)\s+'
    '(?P<wait_ticks>\d+)\s+'
    '(?P<irq_ticks>\d+)\s+'
    '(?P<softirq_ticks>\d+)\s+'
    '(?P<steal_ticks>\d+)\s+'
    '(?P<guest_ticks>\d+)',
)

MEM_PATTERN = re.compile(
    '(?P<label>MEM)\s+' +
    PREFIX_PATTERN +
    '(?P<page_size>\d+)\s+'
    '(?P<phys_pages>\d+)\s+'
    '(?P<free_pages>\d+)\s+'
    '(?P<cache_pages>\d+)\s+'
    '(?P<buffer_pages>\d+)\s+'
    '(?P<slab_pages>\d+)\s+'
    '(?P<dirty_pages>\d+)'
)

NET_UPPER_PATTERN = re.compile(
    '(?P<label>NET)\s+' +
    PREFIX_PATTERN +
    'upper\s+'
    '(?P<tcp_rx>\d+)\s+'
    '(?P<tcp_tx>\d+)\s+'
    '(?P<udp_rx>\d+)\s+'
    '(?P<udp_tx>\d+)\s+'
    '(?P<ip_rx>\d+)\s+'
    '(?P<ip_tx>\d+)\s+'
    '(?P<ip_dx>\d+)\s+'
    '(?P<ip_fx>\d+)'
)

NET_PATTERN = re.compile(
    '(?P<label>NET)\s+' +
    PREFIX_PATTERN +
    '(?P<interface>\S+)\s+'
    '(?P<rx_pkt>\d+)\s+'
    '(?P<tx_pkt>\d+)\s+'
    '(?P<rx_bytes>\d+)\s+'
    '(?P<tx_bytes>\d+)\s+'
    '(?P<speed>\d+)\s+'
    '(?P<duplex_command>\d+)'
)

PRC_PATTERN = re.compile(
    '(?P<label>PRC)\s+' +
    PREFIX_PATTERN +
    '(?P<pid>\d+)\s+'
    '\((?P<name>.+)\)\s+'
    '(?P<state>\S+)\s+'
    '(?P<ticks_per_second>\d+)\s+'
    '(?P<user_ticks>\d+)\s+'
    '(?P<sys_ticks>\d+)\s+'
    '(?P<nice>\d+)\s+'
    '(?P<priority>\d+)\s+'
    '(?P<realtime_priority>\d+)\s+'
    '(?P<scheduling_policy>\d+)\s+'
    '(?P<current_cpu>\d+)\s+'
    '(?P<sleep_avg>\d+)'
)

PRM_PATTERN = re.compile(
    '(?P<label>PRM)\s+' +
    PREFIX_PATTERN +
    '(?P<pid>\d+)\s+'
    '\((?P<name>.+)\)\s+'
    '(?P<state>\S+)\s+'
    '(?P<page_size>\d+)\s+'
    '(?P<virtual_kb>\d+)\s+'
    '(?P<resident_kb>\d+)\s+'
    '(?P<shared_kb>\d+)\s+'
    '(?P<virtual_growth_kb>\d+)\s+'
    '(?P<resident_growth_kb>\d+)\s+'
    '(?P<minor_page_faults>\d+)\s+'
    '(?P<major_page_faults>\d+)'
)

PATTERNS = [CPU_TOTAL_PATTERN, CPU_PATTERN, MEM_PATTERN,
            NET_UPPER_PATTERN, NET_PATTERN, PRC_PATTERN, PRM_PATTERN]

ALL_LABELS = ['CPU', 'cpu', 'MEM', 'NET', 'PRC', 'PRM']


def normalize_point(point):
    # interpret strings into numbers
    for k, v in point.items():
        if v.isdigit():
            point[k] = int(v)

    # convert measurement units
    for k, v in point.items():
        if k[-6:] == '_pages':
            point[k[:-6]] = v * point['page_size']
            del point[k]
        elif k[-6:] == '_ticks':
            point[k[:-6]] = float(v) / point['ticks_per_second']
            del point[k]
        elif k[-3:] == '_kb':
            point[k[:-3]] = v * 1024
            del point[k]

    return point


def parse_output(raw, filter_labels):
    filter_labels = set(filter_labels)
    series = []

    active = False
    for line in raw.split('\n'):
        if line == 'SEP':
            active = True
            continue

        if not active:
            continue

        for pattern in PATTERNS:
            m = re.match(pattern, line)
            if m:
                point = m.groupdict()
                if point['label'] in filter_labels:
                    series.append(normalize_point(point))
                break

    return series


def start(module):
    # clear the file
    cmd = 'rm %s' % ATOP_FILE_NAME
    module.run_command(cmd)

    # start atop as daemon
    cmd = ('daemon -n %(name)s -- atop -w %(file)s %(interval)s' %
           dict(name=UNIQUE_NAME, file=ATOP_FILE_NAME,
                interval=module.params['interval']))

    rc, stdout, stderr = module.run_command(cmd)
    result = dict(changed=True, rc=rc, stdout=stdout, stderr=stderr, cmd=cmd)

    if rc:
        module.fail_json(msg='Failed to start atop', **result)
    else:
        # sleep until file is created
        for timeout in range(10):
            if os.path.exists(ATOP_FILE_NAME):
                break

            module.run_command('sleep 1')

        module.exit_json(**result)


def stop(module):
    # stop atop
    cmd = 'daemon -n %(name)s --stop' % dict(name=UNIQUE_NAME)

    rc, stdout, stderr = module.run_command(cmd)

    if rc:
        module.fail_json(msg='Failed to stop atop', rc=rc, stderr=stderr)

    # grab data
    labels = module.params['labels'] or ALL_LABELS
    cmd = ('atop -r %(file)s -P %(labels)s' %
           dict(file=ATOP_FILE_NAME, labels=','.join(labels)))

    rc, stdout, stderr = module.run_command(cmd)

    try:
        series = parse_output(stdout, labels)
        module.exit_json(series=series)
    except Exception as e:
        module.fail_json(msg=str(e), stderr=stderr, rc=rc)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            command=dict(required=True, choices=['start', 'stop']),
            interval=dict(type='int', default=1),
            labels=dict(type='list'),
        ))

    command = module.params['command']

    if command == 'start':
        start(module)
    elif command == 'stop':
        stop(module)
    else:
        module.fail_json(msg='Unsupported command: %s' % command)


from ansible.module_utils.basic import *  # noqa

if __name__ == '__main__':
    main()
