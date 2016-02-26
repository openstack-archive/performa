#!/usr/bin/python

import re

TEST_STATS = re.compile(
    '\s+queries performed:\s*\n'
    '\s+read:\s+(?P<queries_read>\d+)\s*\n'
    '\s+write:\s+(?P<queries_write>\d+).*\n'
    '\s+other:\s+(?P<queries_other>\d+).*\n'
    '\s+total:\s+(?P<queries_total>\d+).*\n',
    flags=re.MULTILINE | re.DOTALL
)
PATTERNS = [
    r'sysbench (?P<version>[\d\.]+)',
    TEST_STATS,
    r'\s+transactions:\s+(?P<transactions>\d+).*\n',
    r'\s+deadlocks:\s+(?P<deadlocks>\d+).*\n',
    r'\s+total time:\s+(?P<duration>[\d\.]+).*\n',
]
TRANSFORM_FIELDS = {
    'queries_read': int,
    'queries_write': int,
    'queries_other': int,
    'queries_total': int,
    'duration': float,
    'transactions': int,
    'deadlocks': int,
}


def parse_sysbench_oltp(raw):
    result = {}

    for pattern in PATTERNS:
        for parsed in re.finditer(pattern, raw):
            result.update(parsed.groupdict())

    for k in result.keys():
        if k in TRANSFORM_FIELDS:
            result[k] = TRANSFORM_FIELDS[k](result[k])

    return result


def main():
    module = AnsibleModule(
        argument_spec=dict(
            threads=dict(type='int', default=10),
            duration=dict(type='int', default=10),
            mysql_host=dict(default='localhost'),
            mysql_db=dict(default='sbtest'),
            oltp_table_name=dict(default='sbtest'),
            oltp_table_size=dict(type='int', default=100000),
        ))

    cmd = ('sysbench '
           '--test=oltp '
           '--db-driver=mysql '
           '--mysql-table-engine=innodb '
           '--mysql-engine-trx=yes '
           '--num-threads=%(threads)s '
           '--max-time=%(duration)s '
           '--max-requests=0 '
           '--mysql-host=%(mysql_host)s '
           '--mysql-db=%(mysql_db)s '
           '--oltp-table-name=%(oltp_table_name)s '
           '--oltp-table-size=%(oltp_table_size)s '
           'run'
           ) % module.params

    start = int(time.time())
    rc, stdout, stderr = module.run_command(cmd)
    end = int(time.time())

    try:
        parsed = parse_sysbench_oltp(stdout)
        parsed['start'] = start
        parsed['end'] = end

        result = dict(records=[parsed])
        module.exit_json(**result)
    except Exception as e:
        module.fail_json(msg=e, rc=rc, stderr=stderr, stdout=stdout)


from ansible.module_utils.basic import *  # noqa

if __name__ == '__main__':
    main()
