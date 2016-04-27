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

""" Module to create a oslo rpc server """

import logging

import oslo_messaging as messaging
from oslo_config import cfg

log = logging.getLogger(__name__)


class Broker(object):
    rpc_server = None

    def __init__(self, topic, host, handler):
        serializer = messaging.RequestContextSerializer(
                messaging.JsonPayloadSerializer())
        transport = messaging.get_transport(cfg.CONF)
        target = messaging.Target(topic=topic, server=host)
        self.rpc_server = messaging.get_rpc_server(transport, target, handler,
                                                   serializer=serializer)

    def serve(self):
        log.info("starting rpc server")
        self.rpc_server.start()
        self.rpc_server.wait()
