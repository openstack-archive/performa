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


def store_data(mongo_url, mongo_db, records, series):
    LOG.info('Store data to Mongo: %s', mongo_url)

    connection_params = utils.parse_url(mongo_url)
    mongo_client = pymongo.MongoClient(**connection_params)
    db = mongo_client.get_database(mongo_db)

    if records:
        records_collection = db.get_collection('records')
        records_collection.insert_many(records)

    if series:
        series_collection = db.get_collection('series')
        series_collection.insert_many(series)
