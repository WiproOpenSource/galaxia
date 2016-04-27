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
Helper module for OpenStack nova
"""

from oslo_config import cfg
from galaxia.gmiddleware.handler import client
import json

NOVA_OPTS = [
    cfg.StrOpt('nova_endpoint', help='Nova service endpoint'),
]

server_detail = "/servers/detail"


CONF = cfg.CONF
opt_group = cfg.OptGroup(name='gexporter',
                         title='Options for the exporter service')
CONF.register_group(opt_group)
CONF.register_opts(NOVA_OPTS, opt_group)


def get_server_details(token, tenant_id):

    headers = {
        'Content-Type': 'application/json',
        'X-Auth-Token': token
    }
    nova_server_detail_url = client.concatenate_url(
            CONF.gexporter.nova_endpoint+"/"+tenant_id, server_detail)
    try:
        resp = client.http_request("GET", nova_server_detail_url, headers,
                               None, None, None)
        if resp.status_code != 200:
            return False
        else:
            return json.loads(resp.text)
    except Exception as ex:
        raise ex


def create_data(response):
    userid_list = []
    tenantid_list = []
    instanceid_list = []
    metadata_list = []
    servers = response["servers"]
    for i in servers:
        if i["status"] == "ACTIVE":
            userid_list.append(i["user_id"])
            tenantid_list.append(i["tenant_id"])
            instanceid_list.append(i["id"])
            if not i["metadata"] :
                metadata_list.append(None)
            else:
                metadata_list.append(i["metadata"]["metering"])

    return userid_list,tenantid_list,instanceid_list,metadata_list
