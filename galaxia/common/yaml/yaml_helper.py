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
import galaxia.templates as template_data
import os

log = logging.getLogger(__name__)

# Method to create relabel configs


def create_relabel_configs(source_label, regex, target_label, replacement):
    relabel_configs = {}
    relabel_configs.update({'source_labels': [source_label]})
    relabel_configs.update({'regex': regex})
    relabel_configs.update({'target_label': target_label})
    relabel_configs.update({'replacement': replacement})
    return relabel_configs


# Method to set target in prometheus.yml file
def set_target(file_name, job, host, port, protocol, endpoint, instance_key, **drillargs):
    job_exist = False
    job_handle = None
    source_labels_value = ['__address__']
    index = 0
    relabel_configs = {}
    target = host + ":" + port
    log.info("File: %s", file)
    log.info("Target: %s", target)

    if instance_key is not None:
        relabel_configs.update({'source_labels': source_labels_value})
        relabel_configs.update({'regex': target})
        relabel_configs.update({'target_label': 'instance_key'})
        relabel_configs.update({'replacement': instance_key})

    with open(file_name, 'a+') as stream:
        a = yaml.load(stream)
        log.info(a)
        d = {'targets': [target]}

        for i in a['scrape_configs']:
            if i['job_name'] == job:
                job_exist = True
                job_handle = i

            if 'static_configs' in i.keys():
                j = i['static_configs']
                for k in j:
                    if 'targets' in k.keys() and target == k['targets']:
                        return "Target already exists"
            index += 1

        if job_exist:
            job_handle['static_configs'].append({'targets': [target]})
            if instance_key is not None:
                if not 'relabel_configs' in job_handle.keys():
                    job_handle['relabel_configs'] = [relabel_configs]
                else:
                    job_handle['relabel_configs'].append(relabel_configs)
        else:
            a['scrape_configs'].append({'job_name': job})
            a['scrape_configs'][index]['scrape_interval'] = "15s"
            a['scrape_configs'][index]['scrape_timeout'] = "10s"
            a['scrape_configs'][index]['static_configs'] = [{'targets': [target]}]
            if instance_key is not None:
                a['scrape_configs'][index]['relabel_configs'] = [relabel_configs]
            a['scrape_configs'][index]['metric_relabel_configs']= []
            for key, value in drillargs.items():
                relabel_config=create_relabel_configs(value, '(.*)', key, '$1')
                a['scrape_configs'][index]['metric_relabel_configs'].append(relabel_config)
        stream.close()

        with open(file_name, 'w') as outfile:
            outfile.write( yaml.dump(a, default_flow_style=False) )
            outfile.close()


# Method to set SD in prometheus yml file
def set_sd(file_name, job, host, port, protocol, sub_type, **drillargs):
    sd_template = sub_type+".yml"
    file_consul_template = os.path.join(os.path.dirname(template_data.__file__), sd_template)
    with open(file_consul_template) as f:
        newdct = yaml.load(f)
    job_exist = False
    job_handle = None
    index = 0
    server = {}
    target = host+":"+port
    server.update({'server': target})
    with open(file_name,'a+') as stream:
        a = yaml.load(stream)

        for i in a['scrape_configs']:
            if i['job_name'] == job:
                job_exist = True
                job_handle = i
                index += 1
                break
            index += 1

        if job_exist and 'consul_sd_configs' in job_handle.keys():
            job_handle['consul_sd_configs'].append({'server': target})
        elif job_exist and not 'consul_sd_configs' in job_handle.keys():
            job_handle['consul_sd_configs']= server
            job_handle['relabel_configs']= newdct
        else:
            a['scrape_configs'].append({'job_name': job})
            a['scrape_configs'][index]['scrape_interval'] = "15s"
            a['scrape_configs'][index]['scrape_timeout'] = "10s"
            a['scrape_configs'][index]['consul_sd_configs'] = [{'server': target}]
            a['scrape_configs'][index]['relabel_configs'] = newdct
            a['scrape_configs'][index]['metric_relabel_configs']= []
            for key, value in drillargs.items():
                relabel_config=create_relabel_configs(value, '(.*)', key, '$1')
                a['scrape_configs'][index]['metric_relabel_configs'].append(relabel_config)
        stream.close()

        with open(file_name, 'w') as outfile:
            outfile.write( yaml.dump(a, default_flow_style=False) )
            outfile.close()