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

import testtools

from performa.modules import sysbench_oltp as sysbench

OLTP_OUTPUT = '''
sysbench 0.4.12:  multi-threaded system evaluation benchmark

Running the test with following options:
Number of threads: 20

Doing OLTP test.
Running mixed OLTP test
Using Special distribution
Using "BEGIN" for starting transactions
Not using auto_inc on the id column
Threads started!
Time limit exceeded, exiting...
(last message repeated 19 times)
Done.

OLTP test statistics:
    queries performed:
        read:                            9310
        write:                           3325
        other:                           1330
        total:                           13965
    transactions:                        665    (10.94 per sec.)
    deadlocks:                           0      (0.00 per sec.)
    read/write requests:                 12635  (207.79 per sec.)
    other operations:                    1330   (21.87 per sec.)

Test execution summary:
    total time:                          60.8074s
    total number of events:              665
    total time taken by event execution: 1208.0577
    per-request statistics:
         min:                                876.31ms
         avg:                               1816.63ms
         max:                               3792.73ms
         approx.  95 percentile:            2886.19ms

Threads fairness:
    events (avg/stddev):           33.2500/0.70
    execution time (avg/stddev):   60.4029/0.21
'''


class TestSysbench(testtools.TestCase):
    def test_parse_oltp(self):

        expected = {
            'version': '0.4.12',
            'queries_read': 9310,
            'queries_write': 3325,
            'queries_other': 1330,
            'queries_total': 13965,
            'transactions': 665,
            'deadlocks': 0,
            'duration': 60.8074,
        }

        self.assertEqual(expected, sysbench.parse_sysbench_oltp(OLTP_OUTPUT))
