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

from oslo_log import log as logging

from performa.engine import utils

LOG = logging.getLogger(__name__)


def _pick_tasks(tasks, matrix):
    matrix = matrix or {}

    for params in utils.algebraic_product(**matrix):
        for task in tasks:
            parametrized_task = copy.deepcopy(task)
            values = parametrized_task.values()[0]

            if isinstance(values, dict):
                values.update(params)

            yield parametrized_task


def play_setup(runner, setup_playbook):
    runner.run(setup_playbook)


def play_execution(runner, execution_playbook):
    records = []
    series = []

    for play in execution_playbook:
        matrix = play.get('matrix')

        for task in _pick_tasks(play['tasks'], matrix):

            task_play = {
                'hosts': play['hosts'],
                'tasks': [task],
            }
            command_results = runner.run([task_play])

            for command_result in command_results:
                if command_result.get('status') == 'OK':
                    payload = command_result['payload']

                    common = dict(id=utils.make_id(),
                                  host=command_result['host'],
                                  status=command_result['status'],
                                  task=command_result['task'])
                    common.update(payload['invocation']['module_args'])

                    if 'records' in payload:
                        for rec in payload['records']:
                            rec.update(common)
                            records.append(rec)
                            LOG.debug('New record: %s', rec)

                    if 'series' in payload:
                        for rec in payload['series']:
                            rec.update(common)
                            series.append(rec)
                            LOG.debug('New time series: %s', rec)

    return records, series


def add_tag(records, tag):
    for r in records:
        r['tag'] = tag


def play_scenario(runner, scenario, tag):
    records = []
    series = []

    if 'setup' in scenario:
        play_setup(runner, scenario['setup'])

    if 'execution' in scenario:
        execution = scenario['execution']

        records, series = play_execution(runner, execution)
        add_tag(records, tag)
        add_tag(series, tag)

    return records, series
