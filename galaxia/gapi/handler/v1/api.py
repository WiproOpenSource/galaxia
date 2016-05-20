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
Handler to handle Galaxia API request
"""

import datetime
import json
import logging
import os
import uuid

from oslo_config import cfg

from galaxia.common.rpc import client
from galaxia.gdata.common import query_list
from galaxia.gdata.common import sql_helper

from sqlalchemy.exc import SQLAlchemyError

# Register options for the dashboard renderer service
API_SERVICE_OPTS = [
    cfg.StrOpt('rabbitmq_host',
               default='localhost',
               help='The host for the rabbitmq server'),
    cfg.StrOpt('topic',
               default='test',
               help='The  topic for the rabbitmq server'),
    cfg.StrOpt('topic_exporter',
               default='test',
               help='The  exporter topic for the rabbitmq server'),

]

CONF = cfg.CONF
opt_group = cfg.OptGroup(name='gapi', title='Options for the\
                                                    api service')
CONF.register_group(opt_group)
CONF.register_opts(API_SERVICE_OPTS, opt_group)
CONF.set_override('topic', CONF.gapi.topic, opt_group)
CONF.set_override('rabbitmq_host', CONF.gapi.rabbitmq_host, opt_group)
CONF.set_override('topic_exporter', CONF.gapi.topic_exporter, opt_group)
log = logging.getLogger(__name__)


class ApiHandler():

    def delete_dashboard(self, **kwargs):
        name = kwargs['name']
        log.info("Request received to delete %s dashboard" % name)
        log.info("Initializing a client connection")
        try:
            mq_client = client.Client(CONF.gapi.topic, CONF.gapi.rabbitmq_host)
            ctxt = {}
            log.info("Publishing message to rabbitmq")
            mq_client.rpc_client.cast(ctxt, 'delete_graph', message=kwargs)
        except Exception as ex:
            return "A messaging exception has been hit and dashboard creation\
                   has failed"

        return "Dashboard delete request has been successfully accepted"

    def update_dashboard(self, **kwargs):
        """
        Handler to update dashboard
        :param kwargs:
        :return:
        """
        name = kwargs['name']
        if kwargs['names_list'] is None:
            names_list = kwargs['search_type']+"=~"+kwargs['search_string']
        else:
            names_list = ','.join(kwargs['names_list'])
        metrics_list = ','.join(kwargs['metrics_list'])
        d_url = os.getenv('renderer_endpoint') + name
        status = "In Progress"

        create_datetime = str(datetime.datetime.now())

        sql_query = query_list.UPDATE_DASHBOARD
        params = [names_list, metrics_list, create_datetime, name]
        try:
            conn = sql_helper.engine.connect()
            conn.execute(sql_query, params)
        except SQLAlchemyError as ex:
            return "A database exception has been hit and dashboard update has\
                   failed %s" % ex.message

        log.info("Initializing a client connection")
        try:
            mq_client = client.Client(CONF.gapi.topic, CONF.gapi.rabbitmq_host)
            ctxt = {}
            log.info("Publishing message to rabbitmq")
            mq_client.rpc_client.cast(ctxt, 'render_graph', message=kwargs)
        except Exception as ex:
            return "A messaging exception has been hit and dashboard creation has\
                   failed"

        return "Dashboard udpate request has been accepted and the updated\
               dashboard will be available @ %s" % d_url

    def create(self, **kwargs):
        """
        Handler to create Dashboard
        :param kwargs:
        :return: response for the request
        """
        """
        CONF = cfg.CONF
        opt_group = cfg.OptGroup(name='gapi', title='Options for the\
                                                    api service')
        CONF.register_group(opt_group)
        CONF.register_opts(API_SERVICE_OPTS, opt_group)
        CONF.set_override('topic', CONF.gapi.topic, opt_group)
        CONF.set_override('rabbitmq_host', CONF.gapi.rabbitmq_host, opt_group)
        """

        name = kwargs['name']
        if not "names_list" in kwargs.keys() or kwargs['names_list'] is None:
            if "exclude" in kwargs.keys() and kwargs["exclude"]:
                names_list = kwargs['search_type']+"!~"+kwargs['search_string']
            else:
                names_list = kwargs['search_type']+"=~"+kwargs['search_string']
        else:
            names_list = ','.join(kwargs['names_list'])
        metrics_list = ','.join(kwargs['metrics_list'])
        d_url = os.getenv('renderer_endpoint') + name
        status = "In Progress"

        create_datetime = str(datetime.datetime.now())

        sql_query = query_list.INSERT_INTO_DASHBOARD
        params = [name, names_list, metrics_list, d_url, status,
                  create_datetime, create_datetime]
        try:
            conn = sql_helper.engine.connect()
            conn.execute(sql_query, params)
        except SQLAlchemyError as ex:
            return "A database exception has been hit and dashboard creation\
                   has failed %s" % ex.message

        log.info("Initializing a client connection")
        try:
            mq_client = client.Client(CONF.gapi.topic, CONF.gapi.rabbitmq_host)
            ctxt = {}
            log.info("Publishing message to rabbitmq")
            mq_client.rpc_client.cast(ctxt, 'render_graph', message=kwargs)
        except Exception as ex:
            return "A messaging exception has been hit and dashboard creation\
                   has failed"

        return "Dashboard creation request has been accepted and the new\
               dashboard will be available @ %s" % d_url

    def get_metrics(self, query_type):
        """
        Handler to get supported metrics for a unit_type
        :param query_type:
        :return:
        """

        log.info("Request received to get supported metrics for type %s"
                 % query_type)
        conn = sql_helper.engine.connect()
        sql_query = query_list.GET_METRICS
        params = query_type,
        try:
            result = conn.execute(sql_query, params)
        except SQLAlchemyError as ex:
            return "Unable to get the metrics list because of database\
                   exception"

        log.info("Request to get supported metrics for %s successfully\
                 processed" % query_type)

        return json.dumps(dict(result.fetchall()))

    def create_metrics_exporter(self, **kwargs):
        """
        Handler to create metrics exporter
        :param kwargs:
        :return:
        """
        """
        CONF = cfg.CONF
        opt_group = cfg.OptGroup(name='gapi',
                                 title='Options for the api service')
        CONF.register_group(opt_group)
        CONF.register_opts(API_SERVICE_OPTS, opt_group)
        CONF.set_override('topic_exporter', CONF.gapi.topic_exporter,
                          opt_group)
        CONF.set_override('rabbitmq_host', CONF.gapi.rabbitmq_host,
                          opt_group)
        """
        exporter_id = str(uuid.uuid4())
        kwargs['exporter_id'] = exporter_id

        sql_query = query_list.INSERT_INTO_EXPORTER
        params = kwargs['exporter_name'], exporter_id
        try:
            conn = sql_helper.engine.connect()
            conn.execute(sql_query, params)
        except SQLAlchemyError as ex:
            return "A database exception has been hit and metrics exporter has\
                   failed"

        log.info("Initializing a client connection")
        try:
            mq_client = client.Client(CONF.gapi.topic_exporter,
                                  CONF.gapi.rabbitmq_host)
            ctxt = {}
            log.info("Publishing message to rabbitmq")
            mq_client.rpc_client.cast(ctxt, 'export_metrics', message=kwargs)
        except Exception as ex:
            return "A messaging exception has been hit and metrics export\
                   request has failed"

        return "Metrics export request has been successfully accepted"
