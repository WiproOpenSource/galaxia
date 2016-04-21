# Copyright 2016 - Wipro Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and

"""
Handler for listing containers, nodes, dashboards, directories,
exporters
"""
from galaxia.common.prometheus import prometheus_helper
import json
from galaxia.gdata.common import query_list
from galaxia.gdata.common import sql_helper
from sqlalchemy.exc import SQLAlchemyError
import logging

log = logging.getLogger(__name__)


class CatalogueHandler(object):

    def get_units(self, unit_type):
        if unit_type in self._function:
            return self._function[unit_type]()

    @property
    def _function(self):
        return dict((attr, getattr(self, attr))
                    for attr in dir(self)
                    if not attr.startswith('_') and callable(getattr(self, attr
                                                                     )))

    def container(self):
        names_list, hosts_list = prometheus_helper.get_containers_by_hostname()
        dictionary = dict(zip(names_list, hosts_list))
        return json.dumps(dictionary)

    def dashboard(self):
        sql_query = query_list.LIST_DASHBOARD
        conn = sql_helper.engine.connect()
        try:
            result = conn.execute(sql_query)
        except SQLAlchemyError as ex:
            return "Unable to get the dashboard list because of database exception"

        return json.dumps(dict(result.fetchall()))

    def exporter(self):
        sql_query = query_list.LIST_EXPORTER
        conn = sql_helper.engine.connect()
        try:
            result = conn.execute(sql_query)
        except SQLAlchemyError as ex:
            return "Unable to get the exporter list because of database exception"

        return json.dumps(dict(result.fetchall()))
