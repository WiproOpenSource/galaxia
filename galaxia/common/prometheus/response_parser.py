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
import ast
from operator import itemgetter
import itertools

def get_names_list(resp):
    names_list = []
    metrics_list = []
    hosts_list = []
    image_list = []
    id_list = []
    app_framework_list = []
    result_list = json.loads(resp)['data']['result']

    for i in result_list:
        if i['metric'].get('image'):
            names_list.append(i['metric'].get('name'))
            metrics_list.append(i['value'][1])
            hosts_list.append(i['metric'].get('instance').split(':')[0])
            image_list.append(i['metric'].get('image'))
            id_list.append(i['metric'].get('id'))
            if i['metric'].get('application_framework'):
                app_framework_list.append(i['metric'].get('application_framework'))
            else:
                app_framework_list.append('None')

    return names_list, metrics_list, hosts_list, image_list, id_list, app_framework_list


def get_node_name_list(resp):
    temp=[]
    result_list = json.loads(resp)['data']['result']

    for i in result_list:
        del i['value']
        del i['metric']['__name__']
        i['metric']['host']=i['metric']['instance'].split(':')[0]
        temp.append(i['metric'])

    return json.dumps(temp)
'''
def get_node_name_list(resp):
    instance_list = []
    nodename_list = []
    result_list = json.loads(resp)['data']['result']

    for i in result_list:
        instance_list.append(i['metric'].get('instance').split(':')[0])
        nodename_list.append(i['metric'].get('nodename'))

    return instance_list, nodename_list
'''

def get_names_with_status_list(resp, threshold_time):
    names_list = []
    status_list = []
    result_list = json.loads(resp)['data']['result']

    for i in result_list:
        if i['metric'].get('image'):
            names_list.append(i['metric'].get('name'))
            t1 = long(i['value'][0])
            t2 = long(i['value'][1])
            c1 = long(threshold_time)
            if t1-t2 > c1:
                status_list.append('off')
            else:
                status_list.append('on')
    return names_list, status_list


def get_jmx_names_list(resp):
    instance_list = []
    job_list = []
    labels_list = []

    result_list = json.loads(resp)['data']['result']

    #TODO Add implementation for labels_list
    for i in result_list:
        if i['value'][1] == 0:
            instance_list.append(i['metric'].get('instance').split(':')[0])
            job_list.append(i['metric'].get('job'))
    return instance_list, job_list


def get_labels(meter_name, resp):
    labels = []
    result_list = json.loads(resp)['data']['result']

    for i in result_list:
        label_list=[]
        for key,value in i['metric'].iteritems():
            if key == "__name__" : #or key == "instance" or key == "job":
                pass
            else:
                label_list.append({key: value})
        json_obj = {'label': label_list}
        labels.append(json_obj)
    json_obj = {'name': meter_name, 'labels': labels}
    return json.dumps(json_obj)


def get_app_list(resp, argv):
    temp=[]
    result_list = json.loads(resp)['data']['result']
    for i in result_list:
        del i['value']
        del i['metric']['__name__']
        i['metric']['host']=i['metric']['instance'].split(':')[0]
        for j in argv:
            if j in i['metric'].keys():
                del i['metric'][j]
        temp.append(i['metric'])
    return json.dumps(temp)


def get_metrics(resp, unit_type):
    instance_value_list = []
    result_list = json.loads(resp)['data']['result']
    for i in result_list:
        if unit_type is 'container':
            if 'name' in i['metric'].keys():
                instance_key = i['metric'].get('name')
        else:
            instance_key = i['metric'].get('instance_key')
        value = i['value'][1]
        time = i['value'][0]
        instance_value = {"instance_key": instance_key, "value": value, "time": time}
        instance_value_list.append(instance_value)
    return instance_value_list


def get_entities(resp, rfields, subtype):
    result_list = []
    i_result = json.loads(resp.text)['data']['result']
    temp_set =  set()
    temp_list = []
    final_result = []

    for i in i_result:
        del i['value']
        del i['metric']['__name__']
        temp = {}
        for j in rfields:
            if j in i['metric'].keys():
                if j == 'instance' or j == 'node' or j == 'host' :
                    temp[j] = i['metric'][j].split(':')[0]
                else:
                    temp[j]= i['metric'][j]
        result_list.append(temp)

    for i in result_list:
        temp_set.add(json.dumps(i))

    for i in temp_set:
        temp_list.append(ast.literal_eval(i))

    sorted_list = sorted(temp_list, key=itemgetter(subtype))


    for key,value in  itertools.groupby(sorted_list, key=itemgetter(subtype)):
        temp_dict = {}
        l_list = []
        temp_dict[subtype] = key
        for i in value:
            l_list.append(i)
        temp_dict['returnfields'] = l_list
        final_result.append(temp_dict)

    return final_result