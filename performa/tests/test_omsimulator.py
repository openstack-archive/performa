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

from performa.modules import omsimulator


def _read_sample():
    with open('performa/tests/omsimulator_sample.txt') as f:
        return f.read()


class TestOMSimulator(testtools.TestCase):
    def test_parse_client_call(self):
        expected = dict(msg_sent=5313, bytes_sent=14897652, duration=10,
                        msg_sent_bandwidth=531, bytes_sent_bandwidth=1489765)

        self.assertEqual(expected, omsimulator.parse_output(_read_sample()))
