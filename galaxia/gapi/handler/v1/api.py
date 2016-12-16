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
from galaxia.common.prometheus import prometheus_helper
from galaxia.common.prometheus import metrics_helper

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
        names_list = None
        search_string = None
        search_type = None

        # TBD - adding exclude as part of update dashboard
        #exclude = 0

        name = kwargs['name']
        if not "names_list" in kwargs.keys() or kwargs['names_list'] is None:
            search_string = kwargs['search_string']
            search_type = kwargs['search_type']
            #names_list = kwargs['search_type']+"=~"+kwargs['search_string']
        else:
            names_list = ','.join(kwargs['names_list'])
        metrics_list = ','.join(kwargs['metrics_list'])
        d_url = os.getenv('renderer_endpoint') + name
        status = "In Progress"

        create_datetime = str(datetime.datetime.now())

        sql_query = query_list.UPDATE_DASHBOARD
        params = [names_list, metrics_list, search_string, search_type, create_datetime, name]
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
        names_list = None
        search_string = None
        search_type = None
        exclude = 0

        name = kwargs['name']
        if not "names_list" in kwargs.keys() or kwargs['names_list'] is None:
            search_type = kwargs['search_type']
            search_string = kwargs['search_string']
            if "exclude" in kwargs.keys() and kwargs["exclude"]:
                #names_list = kwargs['search_type']+"!~"+kwargs['search_string']
                exclude = 1
            #else:
                #names_list = kwargs['search_type']+"=~"+kwargs['search_string']
        else:
            names_list = ','.join(kwargs['names_list'])

        metrics_list = ','.join(str(kwargs['metrics_list']))
        d_url = os.getenv('renderer_endpoint') + name
        status = "In Progress"

        create_datetime = str(datetime.datetime.now())

        sql_query = query_list.INSERT_INTO_DASHBOARD
        params = [name, names_list, metrics_list, search_string, search_type, d_url, status,
                  create_datetime, create_datetime, exclude]
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

    def get_metrics(self, unit_type, sub_type):
        """
        Handler to get supported metrics for a unit_type
        :param unit_type:
        :param sub_type
        :return:
        """

        log.info("Request received to get supported metrics for unit_type %s and subtype %s" %(unit_type, sub_type) )
        conn = sql_helper.engine.connect()
        sql_query = query_list.GET_METRICS
        params = sub_type
        try:
            result = conn.execute(sql_query, params)
        except SQLAlchemyError as ex:
            return "Unable to get the metrics list because of database\
                   exception"

        log.info("Request to get supported metrics for %s successfully\
                 processed" % sub_type)

        return json.dumps(dict(result.fetchall()))

    def get_sample(self, **kwargs):
        search_string = None
        search_type = None
        if 'search_string' in kwargs and 'search_type' in kwargs:
            search_string = kwargs['search_string']
            search_type = kwargs['search_type']

        meter_name = kwargs['meter_name']
        unit_type = kwargs['unit_type']

        if search_string is None or search_type is None:
            expr = metrics_helper.get_metrics_with_labels(meter_name, None, None)
        else:
            expr = metrics_helper.get_metrics_with_labels(meter_name, search_type, search_string)

        if 'function_type' in meter_name and 'function_time' in meter_name:
            expr = meter_name['function_type']+"("+expr+"["+meter_name['function_time']+"]"+")"

        if 'aggregation_op' in meter_name:
            expr = meter_name['aggregation_op']+"("+expr+")"

        if 'aggregation_over_time' in meter_name and 'aggregation_over_time_value' in meter_name:
            expr = meter_name['aggregation_over_time']+"_over_time"+"("+expr+"["+meter_name['aggregation_over_time_value']+"]"+")"

        if 'aggregation_paramop' in meter_name and 'aggregation_paramval' in meter_name:
            expr = meter_name['aggregation_paramop']+"("+meter_name['aggregation_paramval']+","+"("+expr+")"+")"

        if 'group_by' in meter_name:
            expr =  expr+' by '+"("+meter_name['group_by']+")"

        if 'not_group_by' in meter_name:
            expr = expr + ' without '+"("+meter_name['not_group_by']+")"


        log.info("Expression %s", expr)
        instance_value_list = prometheus_helper.get_metrics(expr, unit_type)
        kwargs['result_list'] = instance_value_list
        return kwargs


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
