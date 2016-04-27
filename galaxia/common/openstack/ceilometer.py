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
Helper module for OpenStack ceilometer
"""

from oslo_config import cfg
from galaxia.gmiddleware.handler import client
import json

CEILO_OPTS = [
    cfg.StrOpt('ceilometer_endpoint', help='Ceilometer service endpoint'),
]

meters = "meters/"

headers = {
        "Content-Type": "application/json"
    }

CONF = cfg.CONF
opt_group = cfg.OptGroup(name='gexporter', title='Options for the exporter\
                                                 service')
CONF.register_group(opt_group)
CONF.register_opts(CEILO_OPTS, opt_group)


def push_metrics(token, ceilometer_data, counter_name):
    json_data = json.dumps(ceilometer_data)
    length = len(json_data)
    headers = {
        "Content-Type": 'application/json',
        'X-Auth-Token': token,
        'Content-Length': length
    }

    ceilomter_url = client.concatenate_url(CONF.gexporter.
                                           ceilometer_endpoint,
                                           meters+counter_name)
    try:
        resp = client.http_request("POST", ceilomter_url, headers, json_data,
                                   None, None)
        if resp.status_code != 200:
            return False
        else:
            return True
    except Exception as ex:
        raise ex
