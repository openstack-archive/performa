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

import copy
import re

from oslo_config import cfg
from oslo_log import log as logging

from performa.engine import ansible_runner
from performa.engine import utils
from performa import executors as executors_classes

LOG = logging.getLogger(__name__)


def run_command(command):
    return ansible_runner.run_command(command, cfg.CONF.hosts)


def _make_test_title(test, params=None):
    s = test.get('title') or test.get('class')
    if params:
        s += ' '.join([','.join(['%s=%s' % (k, v) for k, v in params.items()
                                if k != 'host'])])
    return re.sub(r'[^\x20-\x7e\x80-\xff]+', '_', s)


def _pick_tests(tests, matrix):
    matrix = matrix or {}
    for test in tests:
        for params in utils.algebraic_product(**matrix):
            parametrized_test = copy.deepcopy(test)
            parametrized_test.update(params)
            parametrized_test['title'] = _make_test_title(test, params)

            yield parametrized_test


def play_preparation(preparation):
    ansible_playbook = preparation.get('ansible-playbook')
    if ansible_playbook:
        ansible_runner.run_playbook(ansible_playbook, cfg.CONF.hosts)


def play_execution(execution):
    records = []
    matrix = execution.get('matrix')

    for test in _pick_tests(execution['tests'], matrix):
        executor = executors_classes.get_executor(test)
        command = executor.get_command()

        command_results = run_command(command)
        for command_result in command_results:

            record = dict(id=utils.make_id(),
                          host=command_result['host'],
                          status=command_result['status'])
            record.update(test)

            if command_result.get('status') == 'OK':
                er = executor.process_reply(command_result['payload'])
                record.update(er)

            records.append(record)

    return records


def play_scenario(scenario):
    records = {}

    if 'preparation' in scenario:
        play_preparation(scenario['preparation'])

    if 'execution' in scenario:
        execution = scenario['execution']

        records = play_execution(execution)

    return records
