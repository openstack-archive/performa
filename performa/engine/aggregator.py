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

from oslo_log import log as logging
import pymongo

from performa.engine import utils

LOG = logging.getLogger(__name__)


def aggregate(scenario, mongo_url, db_name, tag):
    if 'aggregation' not in scenario:
        return  # nothing to do

    LOG.info('Running aggregation')

    connection_params = utils.parse_url(mongo_url)
    mongo_client = pymongo.MongoClient(**connection_params)
    db = mongo_client.get_database(db_name)

    aggregation = scenario['aggregation']

    records_collection = db.get_collection('records')
    series_collection = db.get_collection('series')

    for op_group in aggregation:
        for op, op_params in op_group.items():
            if op == 'update':

                select_query = op_params['query']
                values_query = op_params['values']
                values_pipeline = values_query['pipeline']

                select_query['tag'] = tag
                select_query['status'] = 'OK'

                for rec in records_collection.find(select_query):
                    start = rec['start']
                    stop = rec['end']  # todo rename field into 'stop'

                    series_pipeline = [
                        {'$match': {'$and': [
                            {'tag': tag},
                            {'timestamp': {'$gte': start}},
                            {'timestamp': {'$lte': stop}}
                        ]}}
                    ]
                    series_pipeline.extend(values_pipeline)

                    point = next(series_collection.aggregate(series_pipeline))
                    del point['_id']  # to avoid overwriting
                    rec.update(point)

                    records_collection.update_one({'_id': rec['_id']},
                                                  {'$set': point})

                    LOG.debug('Updated record: %s', rec)
