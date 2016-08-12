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
# limitations under the License.

"""
Promdash Handler
"""

import datetime
import logging
import os

from oslo_config import cfg
from sqlalchemy.exc import SQLAlchemyError

from galaxia.common.json import promdash_json as pj
from galaxia.gdata.common import query_list
from galaxia.gmiddleware.handler import client
from galaxia.gdata.common import sql_helper
import importlib

metrics_handlers = {
        'docker': "galaxia.grenderer.handler.docker.prometheus_handler",
        'node': "galaxia.grenderer.handler.node.prometheus_handler",
        'jmx': "galaxia.grenderer.handler.app.jmx.prometheus_handler"
    }

PROMDASH_OPTS = [
    cfg.StrOpt('renderer_db_url',
               default='localhost',
               help='The db_url for renderer server'),
]

query_url = "query"
dashboard_url = "dashboard"
headers = {
        "Content-Type": "application/json"
    }

log = logging.getLogger(__name__)


def delete_dashboard(message):
    name = message['name']
    conn = sql_helper.engine.connect()
    sql_query = query_list.DELETE_DASHBOARD
    sql_query1 = query_list.DELETE_FROM_DASHBOARDS
    params = name
    try:
        conn.execute(sql_query, params)
        conn.execute(sql_query1, params)
    except SQLAlchemyError as ex:
        return "Unable to delete dashboard because of database exception"

    log.info("Request to delete dashboard %s is successfully  processed" % name)


def draw_dashboard(message):
    CONF = cfg.CONF
    opt_group = cfg.OptGroup(name='grenderer',
                             title='Options for the renderer service')
    CONF.register_group(opt_group)
    CONF.register_opts(PROMDASH_OPTS, opt_group)
    CONF.set_override('renderer_db_url', CONF.grenderer.renderer_db_url,
                      opt_group)

    sql_query = query_list.IS_DASHBOARD_PRESENT
    params = message['name']
    param_list = []
    param_list.append(params)

    conn = sql_helper.engine.connect()
    result = conn.execute(sql_query, param_list)
    is_dashboard_present = result.fetchall()

    unit_type = message['unit_type']

    names_list, _ = importlib.import_module(metrics_handlers[unit_type]).\
        get_names_list(message)
    if len(names_list) == 0:
        log.error("No units found for %s for search string %s and search type\
                  %s" % (unit_type, message['search_string'],
                         message['search_type']))
        log.error("Dashboard creation has been aborted for dashboard %s"
                  % message['name'])
        return

    dict1 = pj.create_json(message['name'], names_list,
                           message['metrics_list'], message['unit_type'])
    log.info(dict1)

    if not is_dashboard_present:
        try:
            curr_timestamp = datetime.datetime.now().isoformat()
            sql_query = query_list.INSERT_INTO_DASHBOARDS
            params = [None, message['name'], None, curr_timestamp,
                      curr_timestamp, message['name'], None, 0]
            result = conn.execute(sql_query, params)

        except SQLAlchemyError as e:
            log.error(e.message)
            log.error(e.args)

    prom_dash_request_url = client.concatenate_url(
            os.getenv("renderer_endpoint"), message['name'])

    try:
        resp = client.http_request("PUT", prom_dash_request_url, headers,
                                   dict1, None, None)
    except Exception as ex:
        log.error("Dashboard creation has failed because of http error %s"
                  % ex.message)
        raise ex
    if resp.status_code == 200:
        log.info("Dashboard creation for %s application is successful"
                 % message['name'])
    else:
        log.info("Dashboard creation for %s application is unsuccessful with\
                 http status code %s" % (message['name'], resp.status_code))