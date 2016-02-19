# Copyright (c) 2016 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

from oslo_log import log as logging

from performa.executors import base

LOG = logging.getLogger(__name__)


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


class SysbenchOltpExecutor(base.BaseExecutor):
    def get_command(self):
        cmd = base.CommandLine('sysbench')

        cmd.add('--test', 'oltp')
        cmd.add('--db-driver', 'mysql')
        cmd.add('--mysql-table-engine', 'innodb')
        cmd.add('--mysql-engine-trx', 'yes')
        cmd.add('--num-threads', self.test_definition.get('threads') or 10)
        cmd.add('--max-time', self.get_expected_duration())
        cmd.add('--max-requests', 0)
        cmd.add('--mysql-host', 'localhost')
        cmd.add('--mysql-db', 'sbtest')
        cmd.add('--oltp-table-name', 'sbtest')
        cmd.add('--oltp-table-size',
                self.test_definition.get('table_size') or 100000)
        # cmd.add('--oltp-num-tables',
        #         self.test_definition.get('num_tables') or 10)
        # cmd.add('--oltp-auto-inc', 'off')
        # cmd.add('--oltp-read-only', 'off')
        cmd.add('run')

        return cmd.make()

    def process_reply(self, record):
        stdout = record.get('stdout')
        return parse_sysbench_oltp(stdout)
