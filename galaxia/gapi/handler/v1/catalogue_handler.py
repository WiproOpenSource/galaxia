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
from oslo_config import cfg


# Register options for the api service
CATALOGUE_SERVICE_OPTS = [
    cfg.StrOpt('node',
               default='node_uname_info'
               ),
    cfg.StrOpt('node_remove',
               default=''
               ),
    cfg.StrOpt('docker',
               default='container_last_seen'
               ),
    cfg.StrOpt('docker_remove',
               default=''
               ),
    cfg.StrOpt('tomcat',
               default='catalina_threadpool_maxthreads{name=~"ajp"}'
               ),
    cfg.StrOpt('tomcat_remove',
               default='name'
               ),
    cfg.StrOpt('cassandra',
               default='java_lang_garbagecollector_lastgcinfo_memoryusagebeforegc_max{name="ParNew",key="Par Survivor Space",}'
               ),
     cfg.StrOpt('cassandra_remove',
               default='name,key'
               ),
    cfg.StrOpt('mongodb',
               default='mongodb_connections{state="available"}'
               ),
    cfg.StrOpt('mongodb_remove',
               default='state'
               ),
    cfg.StrOpt('mysql',
               default='mysql_up'
               ),
    cfg.StrOpt('mysql_remove',
               default=''
               ),
    cfg.StrOpt('postgres',
               default='pg_exporter_scrapes_total'
               ),
    cfg.StrOpt('postgres_remove',
               default=''
               )
]

CONF = cfg.CONF
opt_group = cfg.OptGroup(name='catalogue', title='Options for the catalogue service')
CONF.register_group(opt_group)
CONF.register_opts(CATALOGUE_SERVICE_OPTS, opt_group)

CONF.set_override('node', CONF.catalogue.node, opt_group)
CONF.set_override('node_remove', CONF.catalogue.node_remove, opt_group)
CONF.set_override('docker', CONF.catalogue.docker, opt_group)
CONF.set_override('docker_remove', CONF.catalogue.docker_remove, opt_group)
CONF.set_override('tomcat', CONF.catalogue.tomcat, opt_group)
CONF.set_override('tomcat_remove', CONF.catalogue.tomcat_remove, opt_group)
CONF.set_override('cassandra', CONF.catalogue.cassandra, opt_group)
CONF.set_override('cassandra_remove', CONF.catalogue.cassandra_remove, opt_group)
CONF.set_override('mongodb', CONF.catalogue.mongodb, opt_group)
CONF.set_override('mongodb_remove', CONF.catalogue.mongodb_remove, opt_group)
CONF.set_override('mysql', CONF.catalogue.mysql, opt_group )
CONF.set_override('mysql_remove', CONF.catalogue.mysql_remove, opt_group )
CONF.set_override('postgres', CONF.catalogue.postgres, opt_group )
CONF.set_override('postgres_remove', CONF.catalogue.postgres_remove, opt_group )
log = logging.getLogger(__name__)


class CatalogueHandler(object):

    def get_units(self, unit_type, search_string, search_type, subtype):
        if unit_type in self._function:
            return self._function[unit_type](search_string,search_type, subtype)

    @property
    def _function(self):
        return dict((attr, getattr(self, attr))
                    for attr in dir(self)
                    if not attr.startswith('_') and callable(getattr(self, attr
                                                                     )))

    def container(self, search_string, search_type, subtype):
        list1 = ["Name", "Host", "Image", "Id", "application_framework"]
        i=0
        names_list, hosts_list, image_list, id_list, appframework_list = prometheus_helper.get_containers_by_hostname(search_string,search_type)
        return json.dumps([{list1[i]: value for i, value in enumerate(x, i)} for x in zip(names_list,hosts_list,image_list,id_list,appframework_list)])

    def dashboard(self, search_string, search_type, subtype):
        sql_query = query_list.LIST_DASHBOARD
        conn = sql_helper.engine.connect()
        try:
            result = conn.execute(sql_query)
        except SQLAlchemyError as ex:
            return "Unable to get the dashboard list because of database exception"
        k_list = result.keys()
        r_list = []
        r = result.fetchone()
        while r is not None:
            r_list.append(dict(zip(k_list,r)))
            r=result.fetchone()
        temp_json = json.dumps(r_list)
        abc = json.loads(temp_json)

        for x in abc:
            if x['NAMES_LIST'] is not None:
                values = x['NAMES_LIST'].split(',')
                temp1= []
                for i in values:
                    temp1.append(i)
                x['NAMES_LIST'] = temp1

            values = x['METRICS_LIST'].split(',')
            temp2= []
            for i in values:
                temp2.append(i)
            x['METRICS_LIST'] = temp2

        return json.dumps(abc)


       # return json.dumps(dict(result.fetchall()))

    def exporter(self, search_string, search_type, subtype):
        sql_query = query_list.LIST_EXPORTER
        conn = sql_helper.engine.connect()
        try:
            result = conn.execute(sql_query)
        except SQLAlchemyError as ex:
            return "Unable to get the exporter list because of database exception"

        return json.dumps(dict(result.fetchall()))

    def node(self, search_string, search_type, subtype):
        return prometheus_helper.get_names_list(search_string, search_type)

    def app(self, search_string, search_type, subtype):
        if subtype == "tomcat":
            return prometheus_helper.get_apps(CONF.catalogue.tomcat, search_type, search_string,tuple(CONF.catalogue.tomcat_remove.split(',')))
        elif subtype == "cassandra":
            return prometheus_helper.get_apps(CONF.catalogue.cassandra, search_type, search_string,tuple(CONF.catalogue.cassandra_remove.split(',')))
        elif subtype == 'mongodb':
            return prometheus_helper.get_apps(CONF.catalogue.mongodb, search_type, search_string,tuple(CONF.catalogue.mongodb_remove.split(',')))
        elif subtype == 'mysql':
            return prometheus_helper.get_apps(CONF.catalogue.mysql, search_type, search_string,tuple(CONF.catalogue.mysql_remove.split(',')))
        elif subtype == 'postgres':
            return prometheus_helper.get_apps(CONF.catalogue.postgres, search_type, search_string, tuple(CONF.catalogue.postgres_remove.split(',')))
