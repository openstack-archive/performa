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

from collections import namedtuple

from ansible.executor import task_queue_manager
from ansible import inventory
from ansible.parsing import dataloader
from ansible.playbook import play
from ansible.plugins import callback
from ansible.vars import VariableManager
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class MyCallback(callback.CallbackBase):

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'myown'

    def __init__(self, storage, display=None):
        super(MyCallback, self).__init__(display)
        self.storage = storage

    def _store(self, result, status):
        record = dict(host=result._host.get_name(),
                      status=status,
                      task=result._task.get_name(),
                      payload=result._result)
        self.storage.append(record)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        super(MyCallback, self).v2_runner_on_failed(result)
        self._store(result, 'FAILED')

    def v2_runner_on_ok(self, result):
        super(MyCallback, self).v2_runner_on_ok(result)
        self._store(result, 'OK')

    def v2_runner_on_skipped(self, result):
        super(MyCallback, self).v2_runner_on_skipped(result)
        self._store(result, 'SKIPPED')

    def v2_runner_on_unreachable(self, result):
        super(MyCallback, self).v2_runner_on_unreachable(result)
        self._store(result, 'UNREACHABLE')


Options = namedtuple('Options',
                     ['connection', 'password', 'module_path', 'forks',
                      'remote_user',
                      'private_key_file', 'ssh_common_args', 'ssh_extra_args',
                      'sftp_extra_args', 'scp_extra_args', 'become',
                      'become_method', 'become_user', 'verbosity', 'check'])


def _run(play_source, host_list):

    variable_manager = VariableManager()
    loader = dataloader.DataLoader()
    options = Options(connection='smart', password='swordfish',
                      module_path='/path/to/mymodules',
                      forks=100, remote_user='developer',
                      private_key_file=None,
                      ssh_common_args=None, ssh_extra_args=None,
                      sftp_extra_args=None, scp_extra_args=None, become=None,
                      become_method=None, become_user=None, verbosity=100,
                      check=False)
    passwords = dict(vault_pass='secret')

    # create inventory and pass to var manager
    inventory_inst = inventory.Inventory(loader=loader,
                                         variable_manager=variable_manager,
                                         host_list=host_list)
    variable_manager.set_inventory(inventory_inst)

    # create play
    play_inst = play.Play().load(play_source,
                                 variable_manager=variable_manager,
                                 loader=loader)

    storage = []
    callback = MyCallback(storage)

    # actually run it
    tqm = None
    try:
        tqm = task_queue_manager.TaskQueueManager(
            inventory=inventory_inst,
            variable_manager=variable_manager,
            loader=loader,
            options=options,
            passwords=passwords,
            stdout_callback=callback,
        )
        tqm.run(play_inst)
    finally:
        if tqm is not None:
            tqm.cleanup()

    return storage


def run_command(command, host_list):
    hosts = ','.join(host_list) + ','
    # tasks = [dict(action=dict(module='shell', args=command))]
    tasks = [{'command': command}]

    play_source = dict(
        hosts=host_list,
        gather_facts='no',
        tasks=tasks,
    )

    return _run(play_source, hosts)


def run_playbook(playbook, host_list):

    for play_source in playbook:
        hosts = ','.join(host_list) + ','
        play_source['hosts'] = hosts
        play_source['gather_facts'] = 'no'

        _run(play_source, hosts)
