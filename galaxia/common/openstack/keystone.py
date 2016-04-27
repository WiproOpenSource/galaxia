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
Helper module for OpenStack keystone
"""

from oslo_config import cfg
from galaxia.gmiddleware.handler import client
import json

KEYSTONE_OPTS = [
    cfg.StrOpt('keystone_endpoint', help='keystone service endpoint'),
    cfg.StrOpt('username', help='Username to access keystone service'),
    cfg.StrOpt('password', help='Password to access keystone service'),
    cfg.StrOpt('tenant_name', help='Tenant Name'),
]

tokens = "tokens"
tenants = "tenants"

CONF = cfg.CONF
opt_group = cfg.OptGroup(name='gexporter',
                         title='Options for the exporter service')
CONF.register_group(opt_group)
CONF.register_opts(KEYSTONE_OPTS, opt_group)


def validate_token(token):
    headers = {
        "Content-Type": 'application/json',
        'X-Auth-Token': token
    }
    keystone_token_validation_url = client.concatenate_url(
            CONF.gexporter.keystone_endpoint, tenants)
    try:
        resp = client.http_request("GET", keystone_token_validation_url,
                                   headers, None, None, None)
        if resp.status_code != 200:
            return False
        else:
            return True
    except Exception as ex:
        raise ex


def get_token():
    keystone_token_request_url = client.concatenate_url(
            CONF.gexporter.keystone_endpoint, tokens)

    headers = {
        "Content-Type": "application/json"
    }

    auth_data = {
        "auth": {
            "tenantName": CONF.gexporter.tenant_name,
            "passwordCredentials": {
                "username": CONF.gexporter.username,
                "password": CONF.gexporter.password
            }

        }
    }
    resp = client.http_request("POST", keystone_token_request_url, headers,
                               json.dumps(auth_data), None, None)
    json_resp = json.loads(resp.text)
    auth_token = json_resp["access"]["token"]["id"]
    tenant_id = json_resp["access"]["token"]["tenant"]["id"]
    return auth_token, tenant_id
