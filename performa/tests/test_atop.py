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

from performa.modules import atop


def _read_sample():
    with open('performa/tests/atop_sample.txt') as f:
        return f.read()


class TestAtop(testtools.TestCase):
    def test_parse_cpu_total(self):
        expected = [{'cpu_count': 4, 'date': '2016/02/26', 'guest': 0.0,
                     'host': 'host', 'idle': 3.92, 'interval': 1, 'irq': 0.0,
                     'label': 'CPU', 'nice': 0.0, 'softirq': 0.0, 'steal': 0.0,
                     'sys': 0.04, 'ticks_per_second': 100, 'time': '10:01:04',
                     'timestamp': 1456480864, 'user': 0.04, 'wait': 0.0},
                    {'cpu_count': 4, 'date': '2016/02/26', 'guest': 0.0,
                     'host': 'host', 'idle': 3.92, 'interval': 1, 'irq': 0.0,
                     'label': 'CPU', 'nice': 0.0, 'softirq': 0.0, 'steal': 0.0,
                     'sys': 0.04, 'ticks_per_second': 100, 'time': '10:01:05',
                     'timestamp': 1456480865, 'user': 0.04, 'wait': 0.0}]

        self.assertEqual(expected, atop.parse_output(_read_sample(), ['CPU']))

    def test_parse_cpu(self):
        needle = {'cpu_id': 2, 'date': '2016/02/26', 'guest': 0.0,
                  'host': 'host', 'idle': 0.94, 'interval': 1, 'irq': 0.0,
                  'label': 'cpu', 'nice': 0.0, 'softirq': 0.0, 'steal': 0.0,
                  'sys': 0.03, 'ticks_per_second': 100, 'time': '10:01:05',
                  'timestamp': 1456480865, 'user': 0.03, 'wait': 0.0}

        self.assertIn(needle, atop.parse_output(_read_sample(), ['cpu']))

    def test_parse_mem(self):
        expected = [
            {'buffer': 351428608, 'cache': 3317374976, 'date': '2016/02/26',
             'dirty': 0, 'free': 3659939840, 'host': 'host', 'interval': 1,
             'label': 'MEM', 'page_size': 4096, 'phys': 8373075968,
             'slab': 298115072, 'time': '10:01:04', 'timestamp': 1456480864},
            {'buffer': 351428608, 'cache': 3317387264, 'date': '2016/02/26',
             'dirty': 0, 'free': 3659939840, 'host': 'host', 'interval': 1,
             'label': 'MEM', 'page_size': 4096, 'phys': 8373075968,
             'slab': 298115072, 'time': '10:01:05', 'timestamp': 1456480865}]

        self.assertEqual(expected, atop.parse_output(_read_sample(), ['MEM']))

    def test_parse_net(self):
        needle = {'date': '2016/02/26', 'host': 'host', 'interval': 1,
                  'ip_dx': 0, 'ip_fx': 0, 'ip_rx': 0, 'ip_tx': 0,
                  'label': 'NET', 'tcp_rx': 0, 'tcp_tx': 0, 'time': '10:01:04',
                  'timestamp': 1456480864, 'udp_rx': 0, 'udp_tx': 0}

        self.assertIn(needle, atop.parse_output(_read_sample(), ['NET']))

    def test_parse_prc(self):
        needle = {'current_cpu': 2, 'date': '2016/02/26', 'host': 'host',
                  'interval': 1, 'label': 'PRC', 'name': 'dstat', 'nice': 0,
                  'pid': 11014, 'priority': 120, 'realtime_priority': 0,
                  'scheduling_policy': 0, 'sleep_avg': 0, 'state': 'S',
                  'sys': 0.02, 'ticks_per_second': 100, 'time': '10:01:04',
                  'timestamp': 1456480864, 'user': 0.01}

        self.assertIn(needle, atop.parse_output(_read_sample(), ['PRC']))

    def test_parse_prm(self):
        needle = {'date': '2016/02/26', 'host': 'host', 'interval': 1,
                  'label': 'PRM', 'major_page_faults': 0,
                  'minor_page_faults': 751, 'name': 'atop', 'page_size': 4096,
                  'pid': 19929, 'resident': 2019328, 'resident_growth': 0,
                  'shared': 151552, 'state': 'R', 'time': '10:01:05',
                  'timestamp': 1456480865, 'virtual': 17412096,
                  'virtual_growth': 0}

        self.assertIn(needle, atop.parse_output(_read_sample(), ['PRM']))
