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
Module start galaxia exporter service
"""
import logging
import os
import sys

from oslo_config import cfg

from galaxia.common import service
from galaxia.common.rpc import broker
from galaxia.gexporter.controller import controller

# Register options for the galaxia exporter service
API_SERVICE_OPTS = [
    cfg.StrOpt('rabbitmq_host',
               default='localhost',
               help='The host for the rabbitmq server'),
    cfg.IntOpt('rabbitmq_port',
               default='5672',
               help='The  port for the rabbitmq server'),
    cfg.StrOpt('topic',
               default='test',
               help='The topic'),
    cfg.StrOpt('rabbitmq_username',
               default='guest',
               help='The username for the rabbitmq server'),
]

log = logging.getLogger(__name__)


def main():
    service.prepare_service("gexporter", sys.argv)

    CONF = cfg.CONF
    opt_group = cfg.OptGroup(name='gexporter', title='Options for the\
                                                     exporter service')
    CONF.register_group(opt_group)
    CONF.register_opts(API_SERVICE_OPTS, opt_group)
    CONF.set_override('topic', CONF.gexporter.topic, opt_group)
    CONF.set_override('rabbitmq_host', CONF.gexporter.rabbitmq_host, opt_group)
    CONF.set_override('rabbitmq_port', CONF.gexporter.rabbitmq_port, opt_group)
    CONF.set_override('rabbitmq_username', CONF.gexporter.rabbitmq_username,
                      opt_group)

    endpoints = [
        controller.Controller(),
    ]

    log.info('Starting exporter service in PID %s' % os.getpid())

    rpc_server = broker.Broker(CONF.gexporter.topic,
                               CONF.gexporter.rabbitmq_host,
                               endpoints)
    print 'Galaxia Exporter service started in PID %s' % os.getpid()

    rpc_server.serve()
