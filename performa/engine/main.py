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

import os

from oslo_config import cfg
from oslo_log import log as logging
import yaml

from performa.engine import aggregator
from performa.engine import ansible_runner
from performa.engine import config
from performa.engine import player
from performa.engine import report
from performa.engine import storage
from performa.engine import utils

LOG = logging.getLogger(__name__)


def resolve_hosts(scenario, hosts):
    for k, v in hosts.items():
        scenario = scenario.replace('$%s' % k, ','.join(v) + ',')

    return scenario


def main():
    utils.init_config_and_logging(config.MAIN_OPTS)

    scenario_file_path = utils.get_absolute_file_path(
        cfg.CONF.scenario,
        alias_mapper=lambda f: config.SCENARIOS + '%s.yaml' % f)

    scenario_raw = utils.read_file(scenario_file_path)
    scenario_raw = resolve_hosts(scenario_raw, cfg.CONF.hosts)
    scenario = yaml.safe_load(scenario_raw)

    base_dir = os.path.dirname(scenario_file_path)

    tag = cfg.CONF.tag
    if not tag:
        tag = utils.random_string()
        LOG.info('Using auto-generated tag "%s"', tag)

    runner = ansible_runner.AnsibleRunner(remote_user=cfg.CONF.remote_user)

    records, series = player.play_scenario(runner, scenario, tag)

    storage.store_data(cfg.CONF.mongo_url, cfg.CONF.mongo_db, records, series)

    aggregator.aggregate(scenario, cfg.CONF.mongo_url, cfg.CONF.mongo_db, tag)

    report.generate_report(scenario, base_dir, cfg.CONF.mongo_url,
                           cfg.CONF.mongo_db, cfg.CONF.book, tag)


if __name__ == "__main__":
    main()
