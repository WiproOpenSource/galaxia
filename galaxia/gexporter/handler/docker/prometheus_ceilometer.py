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
Creates and schedules the JOB
"""
import datetime
import logging
import time

from apscheduler.schedulers.background import BackgroundScheduler
from oslo_config import cfg

from galaxia.common.openstack import ceilometer
from galaxia.common.openstack import keystone
from galaxia.common.openstack import nova
from galaxia.common.prometheus import prometheus_helper
from galaxia.gdata.common import query_list
from galaxia.gdata.common import sql_helper
from . import prometheus_ceilometer_container_metrics_mapping as pccmm
from sqlalchemy.exc import SQLAlchemyError

CONF = cfg.CONF

EXPORTER_SERVICE_OPTS = [
    cfg.StrOpt('scheduler_db_url',
               default='localhost',
               help='The host for the rabbitmq server'),
]

opt_group = cfg.OptGroup(name='gexporter', title='Options for the renderer\
                                                 service')
CONF.register_group(opt_group)
CONF.register_opts(EXPORTER_SERVICE_OPTS, opt_group)

log = logging.getLogger(__name__)


def create_job(metrics, time_interval, job_id):
    print ("running job with job id %s" % job_id)
    tenant_id = None
    token = None
    is_valid = False
    nova_servers_details = None

    try:
        sql_query = query_list.GET_OPENSTACK_TOKEN
        conn = sql_helper.engine.connect()
        result = conn.execute(sql_query)
        token = result.fetchall()
    except SQLAlchemyError as ex:
        log.error("Exporter has hit a DB error")
        raise ex

    try:
        is_valid = keystone.validate_token(token[0][0])
    except Exception as ex:
        log.warn("Exporter has hit a keystone exception")

    if not is_valid:
        try:
            token, tenant_id = keystone.get_token()
            conn = sql_helper.engine.connect()
            sql_query = query_list.UPDATE_TOKEN
            params = token
            result = conn.execute(sql_query, params)
        except SQLAlchemyError as ex:
            log.error("Exporter has hit a DB error")
            raise ex
        except Exception as ex:
            log.error("Exporter has hit keystone exception")
            raise ex

    try:
        nova_servers_details = nova.get_server_details(token, tenant_id)
    except Exception as ex:
        log.error("Exporter has hit a nova exception")
        raise ex

    userid_list, tenantid_list, instanceid_list, metadata_list = \
        nova.create_data(nova_servers_details)

    mapping_data = pccmm.get_data(metrics)
    counter_name = mapping_data.keys()[0]
    counter_value = mapping_data.values()[0]
    counter_type = mapping_data.keys()[1]
    counter_unit = mapping_data.values()[1]

    print counter_value

    expression = "rate("+counter_value+"{name=~\"nova\"}"+"["+str(time_interval)+"m"+"])"
    print expression
    names_list, metrics_list = prometheus_helper.get_metrics(expression)
    ceilometer_data = generate_final_metrics_data(userid_list, tenantid_list,
                       instanceid_list, metadata_list, names_list, metrics_list,
                       counter_name, counter_type, counter_unit)
    try:
        is_success = ceilometer.push_metrics(token, ceilometer_data, counter_name)
        print is_success
    except Exception as ex:
        log.error("Exporter has hit a ceilometer exception")
        raise ex


def schedule_job(message):
    log.info("Received request to schedule the exporter job %s with job_id %s"
             % (message['exporter_name'], message['exporter_id']))
    metrics_list = message['metrics_list']

    for i in metrics_list:
        scheduler = BackgroundScheduler()
        scheduler.add_jobstore('sqlalchemy', url=CONF.gexporter.scheduler_db_url)
        job_id = message['exporter_id']
        scheduler.add_job(create_job, args=[i, message["time_interval"],
                                            job_id],
                          trigger='interval',
                          minutes=int(message["time_interval"]), id=job_id)
        try:
            print("Starting scheduler")
            scheduler.start()
        except Exception as ex:
            log.error("last cycle of Scheduler has hit an exception")
        """
        try:
            while True:
                print "In infinite loop"
                time.sleep(2)
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
        """


def generate_final_metrics_data(userid_list, tenantid_list, instanceid_list,
                                metadata_list, names_list, metrics_list,
                                counter_name, counter_type, counter_unit):
    ceilomter_data = []
    timestamp = datetime.datetime.now().isoformat()
    k = 0
    for i in names_list:
        l = 0
        for j in instanceid_list:
            if j in i:
                ceilomter_data.append({"counter_name": counter_name,
                                       "counter_type": counter_type,
                                       "counter_unit": counter_unit,
                                       "counter_volume": metrics_list[k],
                                       "project_id": tenantid_list[l],
                                       "resource_id": instanceid_list[l],
                                       "resource_metadata":
                                           {"user_metadata.metering": metadata_list[l]},
                                       "user_id": userid_list[l]})
                break
            l += 1
        k += 1
    print ceilomter_data
    return ceilomter_data
