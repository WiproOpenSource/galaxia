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

# Helper for prometheus

from galaxia.gmiddleware.handler import client
from galaxia.common.prometheus import response_parser

import os
import datetime
import logging


log = logging.getLogger(__name__)

query_url = "query"

headers = {
        "Accept": "application/json"
    }


def get_all_containers():
        prom_request_url = client.concatenate_url(
        os.getenv("aggregator_endpoint"), query_url)
        current_time = str(datetime.datetime.now().isoformat())+"Z"
        query = "container_last_seen"
        payload = {"query": query, "time": current_time}
        resp = client.http_request("GET", prom_request_url, headers, payload,
                                   None, None)
        names_list, _, _, _, _ = response_parser.get_names_list(resp.text)
        return names_list


def get_metrics(expression):
        prom_request_url = client.concatenate_url(
                os.getenv("aggregator_endpoint"), query_url)
        current_time = str(datetime.datetime.now().isoformat())+"Z"
        payload = {"query": expression, "time": current_time}
        resp = client.http_request("GET", prom_request_url, headers, payload,
                                   None, None)
        names_list, metrics_list, _, _, _ = response_parser.get_names_list(resp.text)
        return names_list, metrics_list


def get_containers_by_hostname(search_string, search_type):
        prom_request_url = client.concatenate_url(
        os.getenv("aggregator_endpoint"), query_url)
        current_time = str(datetime.datetime.now().isoformat())+"Z"
        if search_string is None or search_type is None:
            query = "container_last_seen"
        else:
            query = "container_last_seen{"+search_type+"=~"+'"' +\
                search_string+'"'+"}"

        payload = {"query": query, "time": current_time}
        resp = client.http_request("GET", prom_request_url, headers, payload,
                                   None, None)
        names_list, _, hosts_list, image_list, id_list = response_parser.get_names_list(resp.text)
        return names_list, hosts_list, image_list, id_list


def get_names_list(search_string, search_type):

        prom_request_url = client.concatenate_url(os.getenv
                                                  ("aggregator_endpoint"),
                                                  query_url)
        current_time = str(datetime.datetime.now().isoformat())+"Z"
        if search_string is None or search_type is None:
            query = "node_uname_info"
        else:
            query = "node_uname_info{"+search_type+"=~"+'"' + \
                search_string+'"'+"}"
        payload = {"query": query, "time": current_time}
        resp = client.http_request("GET", prom_request_url, headers,
                                   payload, None, None)
        names_list, nodename_list = response_parser.get_node_name_list(resp.text)
        return names_list, nodename_list


def get_containers_by_status(search_string, search_type, time_interval, status, threshold_time):
        prom_request_url = client.concatenate_url(
        os.getenv("aggregator_endpoint"), query_url)
        current_time = str(datetime.datetime.now().isoformat())+"Z"
        if time_interval is None:
            suffix=''
            prefix=''
        else:
            suffix = "["+time_interval+"]"
            prefix = "max_over_time"

        if search_string is None or search_type is None:
            query = prefix+"("+"container_last_seen" + suffix +")"
        else:
            query = prefix+"("+"container_last_seen{"+search_type+"=~"+'"' +\
                search_string+'"'+"}" + suffix + ")"

        #print query

        payload = {"query": query, "time": current_time}
        resp = client.http_request("GET", prom_request_url, headers, payload,
                                   None, None)
        names_list, status_list = response_parser.get_names_with_status_list(resp.text, threshold_time)
        return names_list, status_list

def reload_prometheus_config(host_port):
    url = "http://"+host_port+"/-/reload"
    resp = client.http_request("POST", url, headers, None, None, None)
    if resp.status_code!=200:
        return False
    else:
        return True


def get_labels(meter_name):
    prom_request_url = client.concatenate_url(
        os.getenv("aggregator_endpoint"), query_url)
    current_time = str(datetime.datetime.now().isoformat())+"Z"
    payload = {"query": meter_name, "time": current_time}
    resp = client.http_request("GET", prom_request_url, headers, payload,
                                   None, None)
    #log.info(resp.text)
    labels_list = response_parser.get_labels(meter_name, resp.text)
    return labels_list