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

""" Module to create a oslo rpc client """

import oslo_messaging as messaging
from oslo_messaging import MessagingException
from oslo_config import cfg


class Client(object):
    rpc_client = None

    def __init__(self, topic, host):
        try:
            transport = messaging.get_transport(cfg.CONF)
            target = messaging.Target(topic=topic, server=host)
            self.rpc_client = messaging.RPCClient(transport, target)
        except MessagingException as ex:
            raise ex
