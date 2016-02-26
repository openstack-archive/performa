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

from oslo_config import cfg
from oslo_log import log as logging

from performa.engine import ansible_runner
from performa.engine import utils

LOG = logging.getLogger(__name__)


def run_command(command):
    return ansible_runner.run_command(command, cfg.CONF.hosts)


def _pick_tasks(tasks, matrix):
    matrix = matrix or {}

    for params in utils.algebraic_product(**matrix):
        for task in tasks:
            parametrized_task = copy.deepcopy(task)
            values = parametrized_task.values()[0]

            if isinstance(values, dict):
                values.update(params)

            yield parametrized_task


def play_setup(setup):
    ansible_runner.run_playbook(setup)


def play_execution(execution_playbook):
    records = []

    for play in execution_playbook:
        matrix = play.get('matrix')

        for task in _pick_tasks(play['tasks'], matrix):

            task_play = {
                'hosts': play['hosts'],
                'tasks': [task],
            }
            command_results = ansible_runner.run_playbook([task_play])

            for command_result in command_results:
                if command_result.get('status') == 'OK':
                    record = dict(id=utils.make_id(),
                                  host=command_result['host'],
                                  status=command_result['status'],
                                  task=command_result['task'])
                    payload = command_result['payload']
                    record.update(payload['invocation']['module_args'])
                    record.update(payload)

                    # keep flat values only
                    for k, v in record.items():
                        if isinstance(v, list) or isinstance(v, dict):
                            del record[k]

                    if 'stdout' in record:
                        del record['stdout']

                    LOG.debug('Record: %s', record)
                    records.append(record)

    return records


def tag_records(records, tag):
    for r in records:
        r['tag'] = tag


def play_scenario(scenario, tag):
    records = {}

    if 'setup' in scenario:
        play_setup(scenario['setup'])

    if 'execution' in scenario:
        execution = scenario['execution']

        records = play_execution(execution)
        tag_records(records, tag)

    return records
