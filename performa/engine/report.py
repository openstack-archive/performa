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

import collections
import errno
import functools
import os
import tempfile

import jinja2
from oslo_config import cfg
from oslo_log import log as logging
import pygal
from pygal import style
import pymongo
import yaml

from performa.engine import config
from performa.engine import utils

LOG = logging.getLogger(__name__)


def generate_chart(chart_str, records_collection, doc_folder, tag):
    chart = yaml.safe_load(chart_str)
    pipeline = chart.get('pipeline')
    title = chart.get('title')
    fill = chart.get('fill') or False
    axes = chart.get('axes') or dict(x='x', y='y')

    if tag:
        pipeline.insert(0, {'$match': {'tag': tag}})

    chart_data = records_collection.aggregate(pipeline)

    lines = collections.defaultdict(list)

    table = '''
.. list-table:: %(title)s
   :header-rows: 1

   *
''' % dict(title=title)

    table += ''.join(('     - %s\n' % axes[k]) for k in sorted(axes.keys()))

    y_keys = set(axes.keys()) ^ set('x')

    for chart_rec in chart_data:
        for k in y_keys:
            lines[k].append((chart_rec['x'], chart_rec[k]))
        table += ('   *\n' +
                  '\n'.join('     - %d' % chart_rec[v]
                            for v in sorted(axes.keys())) +
                  '\n')

    xy_chart = pygal.XY(style=style.RedBlueStyle,
                        fill=fill,
                        legend_at_bottom=True,
                        include_x_axis=True,
                        x_title=axes['x'])

    for k in y_keys:
        xy_chart.add(axes[k], lines[k])

    chart_filename = utils.strict(title)
    abs_chart_filename = '%s.svg' % os.path.join(doc_folder, chart_filename)
    xy_chart.render_to_file(abs_chart_filename)

    doc = '.. image:: %s.*\n\n' % chart_filename
    doc += table

    return doc


def _make_dir(name):
    try:
        os.makedirs(name)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def generate_report(scenario, base_dir, mongo_url, db_name, doc_folder,
                    tag=None):
    if 'report' not in scenario:
        return  # nothing to do

    LOG.info('Generate report')

    doc_folder = doc_folder or tempfile.mkdtemp(prefix='performa')

    connection_params = utils.parse_url(mongo_url)
    mongo_client = pymongo.MongoClient(**connection_params)
    db = mongo_client.get_database(db_name)

    records_collection = db.get_collection('records')

    report_definition = scenario['report']
    report_template = report_definition['template']

    _make_dir(doc_folder)

    jinja_env = jinja2.Environment()
    jinja_env.filters['chart'] = functools.partial(
        generate_chart,
        records_collection=records_collection,
        doc_folder=doc_folder,
        tag=tag)

    template = utils.read_file(report_template, base_dir=base_dir)
    compiled_template = jinja_env.from_string(template)
    rendered_template = compiled_template.render()

    index = open(os.path.join(doc_folder, 'index.rst'), 'w+')
    index.write(rendered_template)
    index.close()

    LOG.info('The report is written to %s', doc_folder)


def main():
    utils.init_config_and_logging(config.MAIN_OPTS)

    scenario_file_path = utils.get_absolute_file_path(
        cfg.CONF.scenario,
        alias_mapper=lambda f: config.SCENARIOS + '%s.yaml' % f)

    scenario = utils.read_yaml_file(scenario_file_path)
    base_dir = os.path.dirname(scenario_file_path)

    generate_report(scenario, base_dir, cfg.CONF.mongo_url, cfg.CONF.mongo_db,
                    cfg.CONF.book, cfg.CONF.tag)


if __name__ == "__main__":
    main()
