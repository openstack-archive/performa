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


def generate_chart(chart_str, db, doc_folder, tag,
                   show_chart=True, show_table=True):
    chart = yaml.safe_load(chart_str)
    pipeline = chart.get('pipeline')  # single pipeline
    pipelines = chart.get('pipelines')  # multiple pipelines
    title = chart.get('title')
    fill = chart.get('fill') or False
    axes = chart.get('axes') or dict(x='x', y='y')
    do_round = show_table

    collection_name = chart.get('collection') or 'records'
    collection = db.get_collection(collection_name)

    LOG.debug('Title: %s', title)

    axes_keys = sorted(axes.keys())
    y_keys = set(axes.keys()) ^ set('x')

    chart_data = collections.defaultdict(dict)

    for pl in (pipelines or [pipeline]):
        pl.insert(0, {'$match': {'status': 'OK'}})

        if tag:
            pl.insert(0, {'$match': {'tag': tag}})

        data = collection.aggregate(pl)

        for rec in data:
            if do_round:
                x = int(round(rec['x']))
            else:
                x = rec['x']

            column = chart_data[x]
            column['x'] = x

            for k in y_keys:
                column[k] = column.get(k) or rec.get(k)

    lines = collections.defaultdict(list)

    table = '''
.. list-table:: %(title)s
   :header-rows: 1

   *
''' % dict(title=title)

    table += ''.join(('     - %s\n' % axes[k]) for k in axes_keys)

    for _, chart_rec in sorted(chart_data.items(), key=lambda a: a[0]):
        for k in y_keys:
            if chart_rec[k]:
                lines[k].append((chart_rec['x'], chart_rec[k]))

        values = []
        for v in axes_keys:
            cv = '.' if chart_rec[v] is None else chart_rec[v]
            patt = '     - %%%s' % ('.1f' if isinstance(cv, float) else 's')
            values.append(patt % cv)

        table += ('   *\n' +
                  '\n'.join(values) +
                  '\n')

    xy_chart = pygal.XY(style=style.RedBlueStyle,
                        fill=fill,
                        legend_at_bottom=True,
                        include_x_axis=True,
                        x_title=axes['x'])

    LOG.debug('Lines: %s', lines)

    for k in y_keys:
        xy_chart.add(axes[k], lines[k])

    chart_filename = utils.strict(title)
    abs_chart_filename = '%s.svg' % os.path.join(doc_folder, chart_filename)
    xy_chart.render_to_file(abs_chart_filename)

    doc = ''
    if show_chart:
        doc += '.. image:: %s.*\n\n' % chart_filename

    if show_table:
        doc += table

    return doc


def generate_info(definition_str, db, doc_folder, tag):
    definition = yaml.safe_load(definition_str)
    pipeline = definition.get('pipeline')
    title = definition.get('title')
    fields = definition.get('fields')

    collection_name = definition.get('collection') or 'records'
    collection = db.get_collection(collection_name)

    LOG.debug('Title: %s', title)

    pipeline.insert(0, {'$match': {'status': 'OK'}})

    if tag:
        pipeline.insert(0, {'$match': {'tag': tag}})

    data = [r for r in collection.aggregate(pipeline)]
    if not data:
        LOG.warning('No data returned for info block: %s', title)
        return '**No data**'

    data = data[0]

    table = '''
.. list-table::
   :header-rows: 1

   *
     - attribute
     - value
'''

    for field_name, field_title in sorted(fields.items(), key=lambda a: a[0]):
        value = data[field_name]
        if value is None:
            value = '.'
        patt = ('''   *\n     - %%s\n     - %%%s\n''' %
                ('.1f' if isinstance(value, float) else 's'))
        table += patt % (field_title, value)

    return table


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

    report_definition = scenario['report']
    report_template = report_definition['template']

    LOG.info('Using report template: %s', report_template)

    _make_dir(doc_folder)

    jinja_env = jinja2.Environment()
    jinja_env.filters['chart_and_table'] = functools.partial(
        generate_chart,
        db=db,
        doc_folder=doc_folder,
        tag=tag)
    jinja_env.filters['chart'] = functools.partial(
        generate_chart,
        db=db,
        doc_folder=doc_folder,
        tag=tag,
        show_table=False)
    jinja_env.filters['table'] = functools.partial(
        generate_chart,
        db=db,
        doc_folder=doc_folder,
        tag=tag,
        show_chart=False)
    jinja_env.filters['info'] = functools.partial(
        generate_info,
        db=db,
        doc_folder=doc_folder,
        tag=tag)

    template = utils.read_file(report_template, base_dir=base_dir)
    compiled_template = jinja_env.from_string(template)
    rendered_template = compiled_template.render()

    index = open(os.path.join(doc_folder, 'index.rst'), 'w+')
    index.write(rendered_template)
    index.close()

    LOG.info('The report is written to %s', doc_folder)


def resolve_vars(scenario_template, vars):
    jinja_env = jinja2.Environment()

    compiled_template = jinja_env.from_string(scenario_template)
    rendered_template = compiled_template.render(vars)

    return rendered_template


def main():
    utils.init_config_and_logging(config.MAIN_OPTS)

    scenario_file_path = utils.get_absolute_file_path(
        cfg.CONF.scenario,
        alias_mapper=lambda f: config.SCENARIOS + '%s.yaml' % f)

    scenario_raw = utils.read_file(scenario_file_path)
    scenario_raw = resolve_vars(scenario_raw, cfg.CONF.vars)
    scenario = yaml.safe_load(scenario_raw)
    base_dir = os.path.dirname(scenario_file_path)

    generate_report(scenario, base_dir, cfg.CONF.mongo_url, cfg.CONF.mongo_db,
                    cfg.CONF.book, cfg.CONF.tag)


if __name__ == "__main__":
    main()
