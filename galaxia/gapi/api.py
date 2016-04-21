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

"""Pecan App definition"""

from galaxia.gapi import config as gapi_config
from oslo_config import cfg
import pecan

import sys

# Register options for the api service
API_SERVICE_OPTS = [
    cfg.IntOpt('port',
               default=7777,
               help='The port for the API server'),
    cfg.StrOpt('host',
               default='127.0.0.1',
               help='The listen IP for the API server')
]

CONF = cfg.CONF
opt_group = cfg.OptGroup(name='gapi', title='Options for the api service')
CONF.register_group(opt_group)
CONF.register_opts(API_SERVICE_OPTS, opt_group)


def get_pecan_config():
    # Set up the pecan configuration
    filename = gapi_config.__file__.replace('.pyc', '.py')
    return pecan.configuration.conf_from_file(filename)


def setup_app(config=None):

    if not config:
        config = get_pecan_config()

    app_conf = dict(config.app)

    app = pecan.make_app(
        app_conf.pop('root'),
        force_canonical=False,
        logging=getattr(config, 'logging', {}),
        **app_conf
    )
    return app
