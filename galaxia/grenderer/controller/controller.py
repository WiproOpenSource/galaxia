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

""" RPC handler for Renderer Service """

import sys
import datetime
import os

from oslo_config import cfg
from galaxia.grenderer.handler import root
import logging


# Register options for the aggregator & renderer service
RENDERER_SERVICE_OPTS = [
    cfg.StrOpt('aggregator',
               default='prometheus',
               help='Aggregator for metrics',
               choices='prometheus'),
    cfg.StrOpt('dashboard_handler',
               default='promdash',
               help='Renderer for metrics',
               choices='promdash'),
]

CONF = cfg.CONF
opt_group = cfg.OptGroup(name='grenderer', title='Options for the renderer\
                                                 service')
CONF.register_group(opt_group)
CONF.register_opts(RENDERER_SERVICE_OPTS, opt_group)
CONF.set_override('aggregator', CONF.grenderer.aggregator, opt_group)
CONF.set_override('dashboard_handler', CONF.grenderer.dashboard_handler,
                  opt_group)


class Controller(object):

    def render_graph(self, ctxt, message):
        log = logging.getLogger(__name__)

        log.info("Received dashboard rendering request for %s application"
                 % message['name'])

        root.handler(CONF.grenderer.aggregator, CONF.grenderer.dashboard_handler,
                     message)

    def delete_graph(self, ctxt, message):
        log = logging.getLogger(__name__)

        log.info("Received dashboard deletion request for %s application"
                 % message['name'])

        root.delete_handler(CONF.grenderer.aggregator, CONF.grenderer.dashboard_handler,
                            message)
