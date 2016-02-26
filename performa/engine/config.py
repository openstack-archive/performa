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
from oslo_config import types
import yaml

from performa.engine import utils


SCENARIOS = 'performa/scenarios/'


class Endpoint(types.String):

    def __call__(self, value):
        value = str(value)
        utils.parse_url(value)
        return value

    def __repr__(self):
        return "Endpoint host[:port]"


class Yaml(types.String):

    def __call__(self, value):
        value = str(value)
        try:
            value = yaml.safe_load(value)
        except Exception:
            raise ValueError('YAML value is expected, but got: %s' % value)
        return value

    def __repr__(self):
        return "YAML data"


MAIN_OPTS = [
    cfg.StrOpt('scenario',
               default=utils.env('PERFORMA_SCENARIO'),
               required=True,
               help=utils.make_help_options(
                   'Scenario to play. Can be a file name or one of aliases: '
                   '%s. Defaults to env[PERFORMA_SCENARIO].', SCENARIOS,
                   type_filter=lambda x: x.endswith('.yaml'))),
    cfg.Opt('mongo-url',
            default=utils.env('PERFORMA_MONGO_URL'),
            required=True,
            type=Endpoint(),
            help='Mongo URL, defaults to env[PERFORMA_MONGO_URL].'),
    cfg.StrOpt('mongo-db',
               default=utils.env('PERFORMA_MONGO_DB'),
               required=True,
               help='Mongo DB, defaults to env[PERFORMA_MONGO_DB].'),
    cfg.StrOpt('remote-user',
               default=utils.env('PERFORMA_REMOTE_USER'),
               required=True,
               help='User for connecting to remote systems, '
                    'defaults to env[PERFORMA_REMOTE_USER].'),
    cfg.Opt('hosts',
            type=Yaml(),
            default=utils.env('PERFORMA_HOSTS'),
            required=True,
            help='Hosts inventory definition in YAML format, '
                 'Can be specified via env[PERFORMA_HOSTS].'),
    cfg.StrOpt('book',
               default=utils.env('PERFORMA_BOOK'),
               help='Generate report in ReST format and store it into the '
                    'specified folder, defaults to env[PERFORMA_BOOK]. '),
    cfg.StrOpt('tag',
               default=utils.env('PERFORMA_TAG'),
               help='Tag the execution, defaults to env[PERFORMA_TAG].'),
]


def list_opts():
    yield (None, copy.deepcopy(MAIN_OPTS))
