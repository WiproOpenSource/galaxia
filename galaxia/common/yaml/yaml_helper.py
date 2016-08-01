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

import yaml
import logging

log = logging.getLogger(__name__)


# Method to set target in prometheus.yml file
def set_target(file, job, host, port, protocol, endpoint, instance_key):
    job_exist = False
    job_handle = None
    index = 0
    relabel_configs = {}
    target = host + ":" + port
    log.info("File: %s", file)
    log.info("Target: %s", target)

    if instance_key is not None:
        relabel_configs.update({'source_labels': '[__address__]'})
        relabel_configs.update({'regex': target})
        relabel_configs.update({'target_label': 'instance_key'})
        relabel_configs.update({'replacement': instance_key})

    with open(file,'a+') as stream:
        a = yaml.load(stream)
        log.info(a)
        d = {'targets': [target]}

        for i in a['scrape_configs']:
            if i['job_name'] == job:
                job_exist = True
                job_handle = i

            j = i['target_groups']
            for k in j:
                if target == k['targets']:
                    return "Target already exists"
            index += 1

        if job_exist:
            job_handle['target_groups'].append({'targets': [target]})
            if instance_key is not None:
                if not 'relabel_configs' in job_handle.keys():
                    job_handle['relabel_configs'] = [relabel_configs]
                else:
                    job_handle['relabel_configs'].append(relabel_configs)
        else:
            a['scrape_configs'].append({'job_name': job})
            a['scrape_configs'][index]['scrape_interval'] = "5s"
            a['scrape_configs'][index]['scrape_timeout'] = "10s"
            a['scrape_configs'][index]['target_groups'] = [{'targets': [target]}]
            if instance_key is not None:
                a['scrape_configs'][index]['relabel_configs'] = [relabel_configs]
        stream.close()

        with open(file, 'w') as outfile:
            outfile.write( yaml.dump(a, default_flow_style=False) )
            outfile.close()