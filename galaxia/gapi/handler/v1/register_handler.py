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

from galaxia.gmiddleware.handler import client
import logging
import os
import galaxia.templates as template_data
from galaxia.common.yaml import yaml_helper
#from galaxia.common.paramiko import paramiko_helper
from galaxia.common.prometheus import prometheus_helper
from galaxia.common.prometheus import metrics_parser
from os.path import expanduser
import json
import paramiko
import scp
from oslo_config import cfg


# Register options for the api service
API_SERVICE_OPTS = [
    cfg.StrOpt('username',
               default='vagrant',
               help='The username for the prometheus server host'),
    cfg.StrOpt('password',
               default='vagrant',
               help='The password the prometheus server host'),
    cfg.StrOpt('prometheus_template',
               default='/etc/prometheus/prometheus.yml',
               help='File location of master prometheus template'),
    cfg.StrOpt('pkey',
               help='primary key'),
    cfg.StrOpt('key_filename',
               help='key_filename')
]

CONF = cfg.CONF
opt_group = cfg.OptGroup(name='gapi', title='Options for the api service')
CONF.register_group(opt_group)
CONF.register_opts(API_SERVICE_OPTS, opt_group)

CONF.set_override('username', CONF.gapi.username, opt_group)
CONF.set_override('password', CONF.gapi.password, opt_group)
CONF.set_override('prometheus_template', CONF.gapi.prometheus_template, opt_group)
CONF.set_override('pkey', CONF.gapi.pkey, opt_group)
CONF.set_override('key_filename', CONF.gapi.key_filename, opt_group)


log = logging.getLogger(__name__)

headers = {
        "Accept": "application/json"
    }


class RegisterHandler():

    def register(self, **kwargs):
        log.info(kwargs)
        unit_type = kwargs['unit_type']
        if unit_type in self._function:
            return self._function[unit_type](**kwargs)

    @property
    def _function(self):
        return dict((attr, getattr(self, attr))
                    for attr in dir(self)
                    if not attr.startswith('_') and callable(getattr(self, attr
                                                                     )))

    def app(self, **kwargs):
        return self.onboarding('app', **kwargs)

    def node(self, **kwargs):
        return self.onboarding('node', **kwargs)

    def container(self, **kwargs):
        return self.onboarding('container', **kwargs)

    def sd(self, **kwargs):
        return self.onboarding('sd', **kwargs)

    def check_connectivity(self, target):
        resp = client.http_request("GET", target, headers, None, None, None)
        if resp.status_code!=200:
            log.error("Unable to reach the request resource @ %s" % target)
            return  "failure"
        else:
            log.info("Agent is reachable")

    def update_prometheus_config(self, base_file):
        log.info("Updating prometheus configuration")
        aggregator_host_port = os.getenv('aggregator_endpoint').split('/')[2]
        aggregator_host = aggregator_host_port.split(':')[0]
        #paramiko_helper.loginandcopy(aggregator_host, None, None, base_file,'/etc/prometheus/')#, True, True)
        sshclient = paramiko.SSHClient()
        sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshclient.load_system_host_keys()
        log.info("Aggregator Host: %s", aggregator_host)
        # Currently supporting username/password and key_file based authentication. ToDO add pkey parameter support in connect method
        sshclient.connect(aggregator_host, username=CONF.gapi.username, password=CONF.gapi.password, key_filename=CONF.gapi.key_filename)
        scpclient = scp.SCPClient(sshclient.get_transport())
        scpclient.put(base_file, '/etc/prometheus')


    def onboarding(self, type, **kwargs):
        host = kwargs["host"]
        port = kwargs["port"]
        #protocol = kwargs["protocol"] #TODO to be implemented
        #endpoint = kwargs["endpoint"]  #TODO to be implemented
        endpoint = "/metrics"
        protocol = "http"
        job_name = kwargs["job_name"]
        if type is 'node' or type is 'container':
            instance_key = None
        elif type is 'app':
            instance_key = kwargs["instance_key"]

        if type is 'node' or type is 'container' or type is 'app':
            target = target = protocol+ "://"+host+":"+port+endpoint
        else:
            target = protocol+ "://"+host+":"+port

        # Custom labels #TODO to be implemented

        # checkConnectivity with target host & port
        status = self.check_connectivity(target)
        if status is 'failure':
            return "Unable to reach the agent on target machine @ %s" %target

        # Read the prometheus yaml file, parse it and set job_name, target and save the file back
        base_file = CONF.gapi.prometheus_template
        if type is 'node' or type is 'container' or type is 'app':
            yaml_helper.set_target(base_file, job_name, host, port, protocol, endpoint, instance_key)
        elif type is 'sd':
            sub_type = kwargs['sub_type']
            yaml_helper.set_sd(base_file, job_name, host, port, protocol, sub_type)

        # SCP the updated prometheus file to prometheus host
        self.update_prometheus_config(base_file)

        # Reload Prometheus configuration
        aggregator_host_port = os.getenv('aggregator_endpoint').split('/')[2]
        log.info("Reloading prometheus configuration")
        resp = prometheus_helper.reload_prometheus_config(aggregator_host_port)
        if not resp:
            log.info("Failed to reload prometheus configuration")
            return "Failed to register app"

        return