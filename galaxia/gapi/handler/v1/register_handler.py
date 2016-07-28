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
from galaxia.common.paramiko import paramiko_helper
from galaxia.common.prometheus import prometheus_helper
from galaxia.common.prometheus import metrics_parser
from os.path import expanduser
import json
import paramiko
import scp


log = logging.getLogger(__name__)

headers = {
        "Accept": "application/json"
    }


class RegisterHandler(object):

    def register(self, **kwargs):
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
        host = kwargs["host"]
        port = kwargs["port"]
        #protocol = kwargs["protocol"] #TODO to be implemented
        #endpoint = kwargs["endpoint"]  #TODO to be implemented
        endpoint = "/metrics"
        protocol = "http"
        job_name = kwargs["job_name"]
        target = protocol+ "://"+host+":"+port+endpoint
        #Custom labels #TODO to be implemented

        # checkConnectivity with target host & port
        resp = client.http_request("GET", target, headers, None, None, None)
        if resp.status_code!=200:
            log.error("Unable to reach the request resource @ %s" % target)
            return "Unable to reach the agent on target machine @ %s host and %s port" %[host, port]
        else:
            log.info("Agent is reachable")

        # Read the prometheus yaml file, parse it and set job_name, target and save the file back
        base_file = os.path.join(os.path.dirname(template_data.__file__),
                             "prometheus.yml")
        yaml_helper.set_target(base_file, job_name, host, port, protocol, endpoint)

        # SCP the updated prometheus file to prometheus host
        log.info("Updating prometheus configuration")
        aggregator_host_port = os.getenv('aggregator_endpoint').split('/')[2]
        aggregator_host = aggregator_host_port.split(':')[0]
        #paramiko_helper.loginandcopy(aggregator_host, None, None, base_file,'/etc/prometheus/')#, True, True)
        sshclient = paramiko.SSHClient()
        sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshclient.load_system_host_keys()
        log.info("Aggregator Host: %s", aggregator_host)
        sshclient.connect(aggregator_host, username="vagrant", password="vagrant")
        scpclient = scp.SCPClient(sshclient.get_transport())
        scpclient.put(base_file, '/etc/prometheus')
        #log.info(stderr.readlines())


        # Reload Prometheus configuration
        log.info("Reloading prometheus configuration")
        resp = prometheus_helper.reload_prometheus_config(aggregator_host_port)
        if not resp:
            log.info("Failed to reload prometheus configuration")
            return "Failed to register app"
        #log.info("Prometheus reloading response:  %s", resp.text)

        onboarding_json = metrics_parser.main(target)
        target_directory = os.path.join(expanduser("~"),"galaxia",job_name,host,port)
        if not os.path.exists(target_directory):
             os.makedirs(target_directory)

        log.info("Onboarding json: %s", onboarding_json)

        target_file = os.path.join(target_directory,"onboarding_json.json")
        json.dumps(onboarding_json, target_file)

        return json.dumps(onboarding_json)


    def agent(self):
        print "todo"

    def sd(self):
        print "todo"