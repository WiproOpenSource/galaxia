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
Prometheus response parser
"""
import json

def get_names_list(resp):
    names_list = []
    metrics_list = []
    hosts_list = []
    image_list = []
    id_list = []
    result_list = json.loads(resp)['data']['result']

    for i in result_list:
        if i['metric'].get('image'):
            names_list.append(i['metric'].get('name'))
            metrics_list.append(i['value'][1])
            hosts_list.append(i['metric'].get('instance').split(':')[0])
            image_list.append(i['metric'].get('image'))
            id_list.append(i['metric'].get('id'))

    return names_list, metrics_list, hosts_list, image_list, id_list


def get_node_name_list(resp):
    instance_list = []
    nodename_list = []
    result_list = json.loads(resp)['data']['result']

    for i in result_list:
        instance_list.append(i['metric'].get('instance').split(':')[0])
        nodename_list.append(i['metric'].get('nodename'))

    return instance_list, nodename_list
