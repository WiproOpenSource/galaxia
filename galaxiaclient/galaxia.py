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
Entry point for command invoked through a command line. Currently it
supports the following commands, operations & options:

Commands
* dashboard
* metrics
* exporter

Operations
* create
* list

Options
--name Name of the dashboard to create
--names-list Name list of containers
--metrics-list List of metrics
--search-string String to be searched
--search-type Type of string to be searched
--unit-type Type of unit
--source-system Source of metrics
--target-system Target system for metrics
--time-interval Time interval in which to push metrics
"""

import argparse
import os
import sys
import json

from galaxiaclient.common import cli_utils
from galaxiaclient.common import client
from galaxiaclient.common import format_print


class Catalogue(cli_utils.BaseParser):
    """
    Command to retrieve details about dashboards, exporters, alerts,
    notifications, directories, nodes, containers etc

    Available Commands:

    galaxia catalogue list --unit-type container
    galaxia catalogue list --unit-type dashboard
    galaxia catalogue list --unit-type exporter
    galaxia catalogue list --unit-type node
    """
    headers = {
        "Content-Type": "application/json"
    }

    catalogue_uri = "catalogue"

    def list(self):
        self.parser.add_argument('--unit-type', help='Type of unit valid value\
                                                     is docker', required=True)
        self.parser.add_argument('--search-type', help='search type', required=False)
        self.parser.add_argument('--search-string', help='search string', required=False)
        args = self.parser.parse_args()
        unit_type = vars(args)['unit_type']
        search_type = vars(args)['search_type']
        search_string = vars(args)['search_string']
        data = {'unit_type': unit_type, 'search_type': search_type, 'search_string': search_string}
        galaxia_api_endpoint = os.getenv("galaxia_api_endpoint")
        target_url = client.concatenate_url(galaxia_api_endpoint,
                                            self.catalogue_uri)
        resp = client.http_request('GET', target_url, self.headers, data)
        if unit_type == 'container':
            format_print.format_dict(resp.json(), "keys")
        if unit_type == 'dashboard':
            format_print.format_dict(resp.json(), "keys")
        if unit_type == 'exporter':
            header = ["EXPORTER_NAME", "EXPORTER_ID"]
            format_print.format_dict(resp.json(), header)
        if unit_type == 'node':
            header = ["Instance_Name", "Host_Name"]
            format_print.format_dict(resp.json(), header)


class Directories(cli_utils.BaseParser):
    """
    Command to work with creating, deleting,
    updating directories for dashboards

    Available Commands:

    galaxia directory add --dashboard-list <list_of_dashboards> --name
    <name_of_the_directory>

    doctor directory delete --name <name_of_the_directory>

    galaxia directory update --dashboard-list <list_of_dashboards> --name
    <name_of_the_directory>
    """


class MetricsExporter(cli_utils.BaseParser):
    """
    Command to work with Exporting metrics
    to various third party systems

    Available Commands:

    galaxia exporter create --source-system <source_system> --target-system
    <target_system> --metrics-list <list_of_metrics> --time-interval
    <time_interval> --unit--type <valid value is docker> --exporter-name
    <unique_exporter_name>
    Creates a scheduled job to export metrics  from source system to a target
    system
    """
    headers = {
        "Content-Type": "application/json"
    }

    exporter_uri = "exporter"

    def create(self):
        self.parser.add_argument('--source-system', help='Source system',
                                 required=True)
        self.parser.add_argument('--target-system', help='Target system',
                                 required=True)
        self.parser.add_argument('--metrics-list', help='List of metrics to\
                                                        export', required=True)
        self.parser.add_argument('--time-interval', help='Time interval\
                                        in which to push metrics to target\
                                                         system', required=True)
        self.parser.add_argument('--unit-type', help='Type of unit valid value\
                                                     is docker', required=True)
        self.parser.add_argument('--exporter-name', help='Unique Name for\
                                                    exporter', required=True)

        args = self.parser.parse_args()
        json_data = client.create_request_data(**vars(args))
        galaxia_api_endpoint = os.getenv("galaxia_api_endpoint")
        target_url = client.concatenate_url(galaxia_api_endpoint,
                                            self.exporter_uri)
        resp = client.http_request('POST', target_url, self.headers,
                                   json_data)
        print resp.text


class MetricsCommands(cli_utils.BaseParser):
    """
    Command to work with dashboard metrics
    Available Commands:

    galaxia metrics list --type <type of unit, valid value is docker>
    """
    headers = {
        "Content-Type": "application/json"
    }

    metrics_uri = "metrics"
    sample_uri = "metrics/sample"

    def list(self):
        resp = None
        self.parser.add_argument('--type', help="Type of unit valid values are\
                                containers, nodes", choices=['container'], required=True)
        args = self.parser.parse_args()
        unit_type = vars(args)['type']
        data = {"type": unit_type}
        galaxia_api_endpoint = os.getenv("galaxia_api_endpoint")
        target_url = client.concatenate_url(galaxia_api_endpoint, self.metrics_uri)
        try:
            resp = client.http_request('GET', target_url, self.headers, data)
            headers = ["NAME", "DESCRIPTION"]
            print "List of supported metrics for "+unit_type
            format_print.format_dict(resp.json(), headers)
        except Exception as ex:
            pass

    def sample(self):
        resp = None
        self.parser.add_argument('--type', help="Type of unit valid values are\
                                containers, nodes", choices=['container'], required=True)
        self.parser.add_argument('--search-string', help='Search String', required=False)
        self.parser.add_argument('--search-type', help='Search String', required=False)
        self.parser.add_argument('--meter-name', help='Name of the meter', required=True)
        args = self.parser.parse_args()
        data = {"type": vars(args)['type'], "search_string": vars(args)['search_string'],
                "search_type": vars(args)['search_type'] , "meter_name": vars(args)['meter_name']}
        galaxia_api_endpoint = os.getenv("galaxia_api_endpoint")
        target_url = client.concatenate_url(galaxia_api_endpoint, self.sample_uri)
        try:
            resp = client.http_request('GET', target_url, self.headers, data)
            headers = ["NAME", "VALUE"]
            print "Current "+ vars(args)['meter_name']
            #print "Current "+unit_type
            format_print.format_dict(resp.json(), headers)
        except Exception as ex:
            pass

    def nodes(self):
        print "This is method to expose metrics supported for nodes"


class DashboardCommands(cli_utils.BaseParser):
    """
    Command for working with Monitoring Dashboards

    Available Commands:

    galaxia dashboard create --name <name_of_the_dashboard> --names-list <list_of_units>
                             --metrics-list <list_of_metrics> --unit--type <valid value is docker>
            Creates the monitoring dashboard with the list of units as in list-of-units

    galaxia dashboard create --name <name_of_the_dashboard> --metrics-list <list_of_metrics>
                             --search-string <string_to_search> --search-type <type_of_search_string>
                             --unit--type <valid value is docker>
    for docker supported search string type are instance, image, name
    for node supported search string type are instance, nodename(hostname) and domainname

    """
    url = "gapi"
    headers = {
        "Content-Type": "application/json"
    }

    def create(self):
        self.parser.add_argument('--name', help='Name of the dashboard', required=True)
        self.parser.add_argument('--metrics-list', help='List of \
                                metrics to be displayed on the dashboard',
                                 required=True)
        self.parser.add_argument('--names-list', help='Names list of \
                                units to plot in dashboard')
        self.parser.add_argument('--search-string', help='Search String')
        self.parser.add_argument('--search-type', help='Search String')
        self.parser.add_argument('--unit-type', help='Type of unit, valid value is docker')
        self.parser.add_argument('--exclude', help='Search excluding search string', required=False)
        args = self.parser.parse_args()
        if not (args.names_list or (args.search_string and args.search_type)):
            self.parser.error('add --names-list or (--search-string and --search-type)')

        json_data = client.create_request_data(**vars(args))
        print json_data
        galaxia_api_endpoint = os.getenv("galaxia_api_endpoint")
        target_url = client.concatenate_url(galaxia_api_endpoint, self.url)
        try:
            resp = client.http_request('PUT', target_url, self.headers, json_data)
            print resp.text
        except Exception as ex:
            pass

    def update(self):
        self.parser.add_argument('--name', help='Name of the dashboard',
                                 required=True)
        self.parser.add_argument('--metrics-list', help='List of \
                                metrics to be displayed on the dashboard',
                                 required=True)
        self.parser.add_argument('--names-list', help='Names list of \
                                units to plot in dashboard')
        self.parser.add_argument('--search-string', help='Search String')
        self.parser.add_argument('--search-type', help='Search String')
        self.parser.add_argument('--unit-type', help='Type of unit,\
                                                     valid value is docker')
        self.parser.add_argument('--exclude', help='Search excluding search string', required=False)
        args = self.parser.parse_args()
        if not (args.names_list or (args.search_string and args.search_type)):
            self.parser.error('add --names-list or (--search-string and\
                              --search-type)')

        json_data = client.create_request_data(**vars(args))
        galaxia_api_endpoint = os.getenv("galaxia_api_endpoint")
        target_url = client.concatenate_url(galaxia_api_endpoint, self.url)
        try:
            resp = client.http_request('POST', target_url, self.headers,
                                       json_data)
            print resp.text
        except Exception as ex:
            pass

    def delete(self):
        self.parser.add_argument('--name', help='Name of the dashboard',
                                 required=True)
        args = self.parser.parse_args()
        json_data = client.create_request_data(**vars(args))
        galaxia_api_endpoint = os.getenv("galaxia_api_endpoint")
        target_url = client.concatenate_url(galaxia_api_endpoint, self.url)
        try:
            resp = client.http_request('DELETE', target_url, self.headers,
                                       json_data)
            print resp.text
        except Exception as ex:
            pass


class StatusCommands(cli_utils.BaseParser):
    """
    Command to retrieve availability status of a container

    Available Commands:

    galaxia status list --unit-type container --search-type <image/name> --search-string <search_string>
    --time-interval <in minutes/hours/days/weeks>
    """
    headers = {
        "Content-Type": "application/json"
    }

    status_uri = "status"

    def list(self):
        self.parser.add_argument('--unit-type', help='Type of unit valid value\
                                                     is docker', required=True)
        self.parser.add_argument('--search-type', help='search type', required=False)
        self.parser.add_argument('--search-string', help='search string', required=False)
        self.parser.add_argument('--time-interval', help='Time Interval', required=False)
        args = self.parser.parse_args()
        unit_type = vars(args)['unit_type']
        search_type = vars(args)['search_type']
        search_string = vars(args)['search_string']
        time_interval = vars(args)['time_interval']
        data = {'unit_type': unit_type, 'search_type': search_type, 'search_string': search_string, 'time_interval': time_interval}
        galaxia_api_endpoint = os.getenv("galaxia_api_endpoint")
        target_url = client.concatenate_url(galaxia_api_endpoint,
                                            self.status_uri)
        resp = client.http_request('GET', target_url, self.headers, data)
        if unit_type == 'container':
            #header = ["Container", "Host", "ImageName", "ID"]
            format_print.format_dict(resp.json(), "keys")


class LabelCommands(cli_utils.BaseParser):
    headers = {
        "Content-Type": "application/json"
    }

    status_uri = "label"

    def list(self):
        self.parser.add_argument('--unit-type', help='Type of unit valid value\
                                                     is docker', required=True)
        self.parser.add_argument('--search-type', help='search type', required=False)
        self.parser.add_argument('--search-string', help='search string', required=False)
        self.parser.add_argument('--meter-name', help='Name of the meter', required=True)
        args = self.parser.parse_args()
        unit_type = vars(args)['unit_type']
        search_type = vars(args)['search_type']
        search_string = vars(args)['search_string']
        meter_name = vars(args)['meter_name']
        data = {'unit_type': unit_type, 'search_type': search_type, 'search_string': search_string, 'meter_name': meter_name}
        galaxia_api_endpoint = os.getenv("galaxia_api_endpoint")
        target_url = client.concatenate_url(galaxia_api_endpoint,
                                            self.status_uri)
        resp = client.http_request('GET', target_url, self.headers, data)
        format_print.format_dict(resp.json(), "keys")


class RegisterCommands(cli_utils.BaseParser):
    headers = {
        "Content-Type": "application/json"
    }

    status_uri = "register"

    def agent(self):
        self.parser.add_argument('--unit-type', help='Type of unit valid value\
                                                     is docker', required=True)
        self.parser.add_argument('--host', help='host', required=True)
        self.parser.add_argument('--port', help='port', required=True)
        self.parser.add_argument('--instance-key', help='Name of the meter', required=False)
        self.parser.add_argument('--job-name', help='Name of the meter', required=True)
        args = self.parser.parse_args()
        unit_type = vars(args)['unit_type']
        host = vars(args)['host']
        port = vars(args)['port']
        job_name = vars(args)['job_name']
        instance_key =  vars(args)['instance_key']
        data = {'unit_type': unit_type, 'host': host, 'port': port, 'job_name': job_name, 'instance_key': instance_key }
        galaxia_api_endpoint = os.getenv("galaxia_api_endpoint")
        target_url = client.concatenate_url(galaxia_api_endpoint,
                                            self.status_uri)
        resp = client.http_request('POST', target_url, self.headers, json.dumps(data))
        format_print.format_dict(resp.json(), "keys")


def main():
    """
    This is the galaxia client help manual

    Supported Commands:

    galaxia help
            Display help

    galaxia --version
            Display version of galaxia client

    galaxia metrics list --type <value>
            List supported metrics, valid value is "container"

    galaxia dashboard create --name <name_of_the_dashboard>
                             --names-list <list_of_system_units>
                             --metrics-list <list_of_metrics>
                             --unit--type <valid value is docker>
            Creates monitoring dashboard using the names

    galaxia dashboard create --name <name_of_the_dashboard> --metrics-list <list_of_metrics>
                             --search-string <string_to_search> --search-type <type_of_search_string>
                             --unit-type <valid value is docker> --exclude <valid value is 1>
            Creates monitoring dashboard using the search string and search type. Here exclude is an
            optional flag, setting exclude to 1 will plot dashboard for all except the search string

    galaxia exporter create --source-system <source_system> --target-system <target_system>
                            --metrics-list <list_of_metrics> --time-interval <time_interval>
                            --unit--type <valid value is docker> --exporter-name <unique_exporter_name>
            Creates a scheduled job to export metrics to a target system

    galaxia catalogue list --unit-type container
            List all the currently monitored containers
    galaxia catalogue list --unit-type dashboard
            List all created dashboards
    galaxia catalogue list --unit-type exporter
            List all created exporters
    galaxia catalogue list --unit-type node
            List all the currently monitored nodes
    galaxia status list --unit-type container --search-type <image/name> --search-string <search_string>
    --time-interval <in minutes/hours/days/weeks>
            Command to retrieve availability status of a container
    """
    parser = argparse.ArgumentParser(prog="galaxiaclient",
                                     description="galaxia helper manual",
                                     usage=main.__doc__)

    modules = {
        "dashboard": DashboardCommands,
        "metrics": MetricsCommands,
        "exporter": MetricsExporter,
        "catalogue": Catalogue,
        "status": StatusCommands,
        "register": RegisterCommands,
        "label": LabelCommands
    }

    options = modules.keys()

    parser.add_argument('module', choices=options, metavar='')
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s v1.0',
                        help='Display galaxia version')

    argument, _ = parser.parse_known_args()

    module = vars(argument).get('module')

    if module in modules:
        modules[module](parser)
    else:
        print main.__doc__


if __name__ == '__main__':
    sys.exit(main())
